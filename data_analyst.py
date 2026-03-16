"""
data_analyst.py
Conversational BI analyst — Natural Language → SQL → DuckDB → Insight + Chart spec.

Pipeline:
  1. LLM generates SQL from user question + schema
  2. DuckDB executes SQL against in-memory DataFrames
  3. LLM interprets results + optionally returns chart spec
  4. Caller renders chart with Plotly
"""

from openai import OpenAI
import duckdb
import pandas as pd
import json
import re
import logging

log = logging.getLogger("data_analyst")
MODEL = "anthropic/claude-sonnet-4-5"

# ── Full schema (injected into every prompt) ───────────────────────────────────
FULL_SCHEMA = """
You have access to these DuckDB tables (already registered):

TABLE: membership
  member_id       VARCHAR   -- e.g. M00001
  brand           VARCHAR   -- Genesis Health + Fitness | Ninja Parc | Jump Swim Schools | Belgravia Kids Swim
  location        VARCHAR
  membership_type VARCHAR   -- Casual | Monthly | Annual | Family | Student | Senior
  join_date       DATE
  cancel_date     DATE      -- NULL if still active
  active          BOOLEAN
  monthly_fee     DOUBLE
  age_group       VARCHAR   -- 18-25 | 26-35 | 36-45 | 46-55 | 55+
  gender          VARCHAR   -- M | F | Other
  nps_score       INTEGER   -- 0-10

TABLE: sales
  sale_id         VARCHAR
  brand           VARCHAR
  location        VARCHAR
  sale_date       DATE
  product         VARCHAR   -- New Membership | Renewal | Personal Training | Merchandise | Supplement | Event
  amount          DOUBLE
  channel         VARCHAR   -- Google Ads | Facebook | Instagram | Email | Referral | Walk-in | SEO
  staff_id        VARCHAR
  month           VARCHAR   -- YYYY-MM
  quarter         VARCHAR   -- Q1 2023 etc.

TABLE: capacity
  session_id      VARCHAR
  brand           VARCHAR
  location        VARCHAR
  class           VARCHAR   -- Yoga | Spin | HIIT | Pilates | Boxing | Aqua Aerobics | Swim Lesson | Ninja Course
  date            DATE
  day_of_week     VARCHAR
  hour            INTEGER   -- 6-20
  capacity        INTEGER
  booked          INTEGER
  attended        INTEGER
  utilisation_pct DOUBLE
  no_show_rate    DOUBLE
  instructor_id   VARCHAR
  month           VARCHAR

TABLE: marketing
  campaign_id     VARCHAR
  brand           VARCHAR
  channel         VARCHAR
  campaign_name   VARCHAR
  month           VARCHAR
  spend           DOUBLE
  impressions     INTEGER
  clicks          INTEGER
  leads           INTEGER
  conversions     INTEGER
  cpc             DOUBLE
  cpl             DOUBLE
  cpa             DOUBLE
  roas            DOUBLE

TABLE: profits
  month                VARCHAR
  quarter              VARCHAR
  brand                VARCHAR
  location             VARCHAR
  revenue_membership   DOUBLE
  revenue_pt           DOUBLE
  revenue_retail       DOUBLE
  revenue_events       DOUBLE
  total_revenue        DOUBLE
  cost_staff           DOUBLE
  cost_lease           DOUBLE
  cost_utilities       DOUBLE
  cost_equipment       DOUBLE
  cost_insurance       DOUBLE
  cost_marketing       DOUBLE
  cost_maintenance     DOUBLE
  cost_admin           DOUBLE
  cost_instructor      DOUBLE
  total_costs          DOUBLE
  gross_profit         DOUBLE
  profit_margin_pct    DOUBLE
  ebitda               DOUBLE

RULES:
- Use standard DuckDB SQL syntax
- Date columns support strftime, date_trunc, EXTRACT
- For BOOLEAN active: use active = TRUE or active = FALSE
- Always LIMIT results to 200 rows max unless doing aggregations
- Column names are lowercase with underscores exactly as shown above
- Do NOT use backticks; use double-quotes for identifiers if needed
"""

SYSTEM_SQL = f"""You are a senior BI analyst at Belgravia Health & Fitness. 
Your job: given a natural language question, write ONE valid DuckDB SQL query that answers it.

{FULL_SCHEMA}

Respond with ONLY a JSON object — no markdown, no backticks, no explanation:
{{
  "sql": "SELECT ... FROM ... WHERE ... GROUP BY ... ORDER BY ... LIMIT ...",
  "needs_chart": true or false,
  "chart_type": "bar|line|scatter|pie|area|table" or null,
  "x_col": "column name for x axis" or null,
  "y_col": "column name for y axis" or null,
  "color_col": "column for colour grouping" or null,
  "chart_title": "descriptive title" or null
}}

If the answer is a single number/metric set needs_chart=false.
If the answer is a list/trend/comparison set needs_chart=true.
"""

SYSTEM_INTERPRET = """You are a Senior BI Analyst at Belgravia Health & Fitness.
Given a user's question, the SQL that was run, and the result data, 
write a sharp 2-4 sentence business interpretation.
Be specific — reference actual numbers from the data.
End with one actionable recommendation.
Keep it concise and executive-ready."""


def _build_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")


def _call_llm(client: OpenAI, system: str, user: str, max_tokens: int = 800) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"LLM error: {e}")
        raise RuntimeError(f"LLM call failed: {e}")


def _extract_json(raw: str) -> dict:
    """Robustly extract a JSON object from LLM output."""
    raw = raw.strip()
    # Strip markdown fences
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"No JSON found in: {raw[:300]}")


def register_tables(conn: duckdb.DuckDBPyConnection, dataframes: dict) -> None:
    """Register all DataFrames as DuckDB views."""
    for name, df in dataframes.items():
        conn.register(name, df)


def nl_to_sql(api_key: str, question: str, conversation_history: list[dict]) -> dict:
    """
    Translate natural language question to SQL + chart spec.
    Uses conversation history for context.
    Returns parsed JSON dict with keys: sql, needs_chart, chart_type, x_col, y_col, color_col, chart_title
    """
    client = _build_client(api_key)

    # Build conversation context string
    ctx = ""
    if conversation_history:
        recent = conversation_history[-6:]  # last 3 exchanges
        ctx_parts = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            ctx_parts.append(f"{role}: {msg['content'][:300]}")
        ctx = "CONVERSATION CONTEXT (for pronoun/reference resolution):\n" + "\n".join(ctx_parts) + "\n\n"

    prompt = f"{ctx}Current question: {question}"
    raw = _call_llm(client, SYSTEM_SQL, prompt, max_tokens=600)
    return _extract_json(raw)


def execute_sql(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    """Execute SQL on DuckDB and return a DataFrame."""
    try:
        result = conn.execute(sql).fetchdf()
        return result
    except Exception as e:
        raise RuntimeError(f"SQL execution error: {e}\nSQL: {sql}")


def interpret_results(api_key: str, question: str, sql: str, df: pd.DataFrame) -> str:
    """Ask LLM to interpret query results as a business narrative."""
    client = _build_client(api_key)

    # Summarise data for the LLM (avoid huge payloads)
    if len(df) > 30:
        data_summary = f"(showing top 30 of {len(df)} rows)\n{df.head(30).to_string(index=False)}"
    else:
        data_summary = df.to_string(index=False)

    prompt = f"""Question: {question}

SQL executed:
{sql}

Query result:
{data_summary}

Provide a sharp business interpretation."""

    return _call_llm(client, SYSTEM_INTERPRET, prompt, max_tokens=400)


def chat_turn(
    api_key: str,
    question: str,
    dataframes: dict,
    conversation_history: list[dict],
) -> dict:
    """
    Full pipeline for one conversational turn.

    Returns:
    {
      "sql": str,
      "data": pd.DataFrame,
      "interpretation": str,
      "chart_spec": dict | None,   # contains chart_type, x_col, y_col, color_col, chart_title
      "error": str | None,
      "row_count": int,
    }
    """
    # 1. Create fresh DuckDB connection and register tables
    conn = duckdb.connect(":memory:")
    register_tables(conn, dataframes)

    result = {
        "sql": "",
        "data": pd.DataFrame(),
        "interpretation": "",
        "chart_spec": None,
        "error": None,
        "row_count": 0,
    }

    try:
        # 2. NL → SQL + chart spec
        spec = nl_to_sql(api_key, question, conversation_history)
        sql = spec.get("sql", "").strip()
        if not sql:
            raise ValueError("LLM returned empty SQL")
        result["sql"] = sql

        # 3. Execute SQL
        df = execute_sql(conn, sql)
        result["data"] = df
        result["row_count"] = len(df)

        # 4. Interpret results
        result["interpretation"] = interpret_results(api_key, question, sql, df)

        # 5. Chart spec (if applicable)
        if spec.get("needs_chart") and len(df) > 0:
            result["chart_spec"] = {
                "chart_type":  spec.get("chart_type", "bar"),
                "x_col":       spec.get("x_col"),
                "y_col":       spec.get("y_col"),
                "color_col":   spec.get("color_col"),
                "chart_title": spec.get("chart_title", question[:80]),
            }

    except Exception as e:
        log.error(f"chat_turn error: {e}")
        result["error"] = str(e)

    finally:
        conn.close()

    return result