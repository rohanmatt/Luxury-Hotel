"""
ai_agent.py
BI insight agent — drives parallel LLM analysis across dashboard sections.
Uses OpenRouter with anthropic/claude-sonnet-4-5 via OpenAI-compatible client.
"""

from openai import OpenAI
import concurrent.futures
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ai_agent")

MODEL = "anthropic/claude-sonnet-4-5"


def _build_client(api_key: str) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def _call_llm(client: OpenAI, system: str, user: str, max_tokens: int = 600) -> str:
    """Single blocking LLM call — safe to run in a thread."""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.4,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"LLM error: {e}")
        return f"⚠️ LLM unavailable: {e}"


# ── Parallel insight generation ────────────────────────────────────────────────

SYSTEM_BI = """You are a Senior Business Intelligence Analyst at Belgravia Health & Fitness 
(brands: Genesis Health + Fitness, Ninja Parc, Jump Swim Schools, Belgravia Kids Swim).
Your job is to deliver sharp, executive-ready insights from KPI summaries.
Be concise, specific, and action-oriented. Use bullet points. Max 5 bullets."""


def get_parallel_insights(api_key: str, kpi_blocks: dict[str, str]) -> dict[str, str]:
    """
    Run multiple LLM insight calls in parallel using ThreadPoolExecutor.

    Args:
        api_key: OpenRouter API key
        kpi_blocks: {section_name: kpi_summary_text}

    Returns:
        {section_name: insight_text}
    """
    client = _build_client(api_key)
    results = {}

    def _task(name_prompt):
        name, prompt = name_prompt
        log.info(f"[Parallel] Starting insight for: {name}")
        result = _call_llm(client, SYSTEM_BI, prompt)
        log.info(f"[Parallel] Completed insight for: {name}")
        return name, result

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(kpi_blocks)) as executor:
        futures = executor.map(_task, kpi_blocks.items())
        for name, insight in futures:
            results[name] = insight

    return results


# ── LLM-powered dynamic dashboard spec ────────────────────────────────────────

SYSTEM_DASHBOARD = """You are a BI dashboard architect at Belgravia Health & Fitness.
Given a user's natural language question and a data summary, respond ONLY with a JSON object 
(no markdown, no backticks) specifying how to visualise the answer.

JSON schema:
{
  "title": "...",
  "chart_type": "bar|line|scatter|pie|table|metric",
  "x": "column_name or null",
  "y": "column_name or null",
  "group_by": "column_name or null",
  "filter": {"column": "value"} or null,
  "aggregation": "sum|mean|count|pct",
  "insight": "one sentence interpretation",
  "sql_hint": "pseudo-SQL for this query"
}"""


def get_dashboard_spec(api_key: str, question: str, data_schema: str) -> dict:
    """Ask LLM to generate a dashboard specification from a natural language question."""
    import json
    client = _build_client(api_key)
    prompt = f"""Data schema available:\n{data_schema}\n\nUser question: {question}"""
    raw = _call_llm(client, SYSTEM_DASHBOARD, prompt, max_tokens=400)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON from response
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"error": raw}


# ── Narrative report generation ────────────────────────────────────────────────

SYSTEM_REPORT = """You are writing an executive BI report for Belgravia Health & Fitness leadership.
Write in clear, professional prose. Structure: 1 paragraph context, 3-5 key findings, 1 paragraph 
recommendations. Be specific with numbers from the provided KPIs."""


def get_executive_report(api_key: str, all_kpis: str) -> str:
    """Generate a full executive narrative report from combined KPI data."""
    client = _build_client(api_key)
    return _call_llm(client, SYSTEM_REPORT, all_kpis, max_tokens=800)