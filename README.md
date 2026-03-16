# 💪 Belgravia Health & Fitness — BI Intelligence Platform

> A Streamlit demo application built for the **Business Intelligence Analyst (Health & Fitness)** role at Belgravia Health & Fitness.  
> Covers: Membership · Sales · Capacity · Marketing · Profits · AI Insights · AI Dashboard (Chat with Data)

---

## 📁 Project Structure

```
belgravia_bi/
├── app.py              # Main Streamlit application — all 7 tabs, UI, session state
├── generate_data.py    # Synthetic data factory — 5 datasets, ~17,000 rows
├── ai_agent.py         # Parallel LLM insight engine + executive report generator
├── data_analyst.py     # Conversational NL → SQL → DuckDB → Chart pipeline
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

**requirements.txt**
```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
openai>=1.30.0
duckdb>=0.10.0
```

**AI Features (Tabs 6 & 7)**  
Get a free key at [openrouter.ai](https://openrouter.ai) → paste into the sidebar **OpenRouter API Key** field.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       Streamlit Frontend                          │
│   Sidebar (brand filter · year · API key)                        │
│   KPI strip (7 headline metrics)                                  │
│   7 Tabs  ·  Plotly charts  ·  Chat UI  ·  Session state         │
└───────────────────────┬──────────────────────────────────────────┘
                        │
               ┌────────▼────────┐
               │    app.py       │  Entry point — orchestrates all modules,
               │  (entry point)  │  filtering, layout, chart rendering
               └──┬──────────┬───┘
                  │          │
       ┌──────────▼──┐  ┌────▼────────────┐  ┌──────────────────┐
       │generate_    │  │  ai_agent.py    │  │ data_analyst.py  │
       │data.py      │  │                 │  │                  │
       │             │  │ Parallel LLM    │  │ NL → SQL         │
       │ 5 synthetic │  │ calls via       │  │ DuckDB execute   │
       │ DataFrames  │  │ ThreadPoolExec  │  │ Interpret result │
       │ @cached     │  │                 │  │ Chart spec JSON  │
       └──────────────┘  └────────┬────────┘  └────────┬─────────┘
                                  │                    │
                         ┌────────▼────────────────────▼───────┐
                         │          OpenRouter API              │
                         │  model: anthropic/claude-sonnet-4-5  │
                         │  base_url: openrouter.ai/api/v1      │
                         │  client: openai.OpenAI(...)          │
                         └──────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Static Dashboards (Tabs 1–5)

```
generate_data.py
  └─ load_all()                   ← called once, cached via @st.cache_data
       ├─ generate_membership()   → 5,000 rows
       ├─ generate_sales()        → 8,000 rows
       ├─ generate_capacity()     → 3,000 rows
       ├─ generate_marketing()    →   500 rows
       └─ generate_profits()      → ~1,152 rows (24 months × 4 brands × locations)

app.py
  └─ Sidebar filters (brand, year) applied to all DataFrames
       └─ Pandas aggregations → Plotly figures → st.plotly_chart()
```

### 2. AI Insights — Tab 6 (Parallel LLM)

```
User clicks "Generate All Insights"
  └─ 5 KPI summary strings built from filtered DataFrames
       └─ ai_agent.get_parallel_insights(api_key, kpi_blocks)
            └─ ThreadPoolExecutor(max_workers=5)
                 ├─ Thread 1 → Membership insight
                 ├─ Thread 2 → Sales insight
                 ├─ Thread 3 → Capacity insight
                 ├─ Thread 4 → Marketing insight
                 └─ Thread 5 → Profits insight
            ~4–6 seconds total vs ~20+ seconds sequential
  └─ ai_agent.get_executive_report() → 1 narrative prose report
  └─ Insight boxes + executive report rendered
```

### 3. AI Dashboard — Tab 7 (NL → SQL → DuckDB → Chart)

```
User types question OR clicks a chip button
          │
          ▼
  ┌───────────────────────────────────────────────┐
  │  Queue pattern (Streamlit-safe):              │
  │  chip click  → sets dash_queue → st.rerun()  │
  │  next rerun  → dash_queue picked up first     │
  │  Enter btn   → calls run_question() directly  │
  └───────────────────────────────────────────────┘
          │
          ▼
  data_analyst.chat_turn(api_key, question, dataframes, history)
          │
          ├─ Step 1: nl_to_sql()
          │    └─ LLM receives: full 5-table schema
          │                   + last 6 messages (conversation context)
          │                   + current question
          │    └─ Returns JSON:
          │         { sql, needs_chart, chart_type, x_col, y_col, color_col, chart_title }
          │
          ├─ Step 2: execute_sql()
          │    └─ duckdb.connect(":memory:")
          │    └─ All 5 DataFrames registered as views
          │    └─ conn.execute(sql).fetchdf()  → pandas DataFrame
          │
          └─ Step 3: interpret_results()
               └─ LLM receives: question + sql + result rows (max 30 shown)
               └─ Returns: 2–4 sentence business narrative + recommendation

  Result stored in st.session_state.dash_history
  UI renders per turn:
    user bubble → assistant bubble → Plotly chart (full width)
    → SQL expander | Data table expander (side by side)
```

---

## 🖥️ UI Flow

```
App loads
  │
  ├─ Sidebar
  │    ├─ Brand filter (multiselect — all 4 brands)
  │    ├─ Year filter (All / 2023 / 2024)
  │    └─ OpenRouter API Key (unlocks Tabs 6 & 7)
  │
  ├─ KPI Strip (always visible, 7 metrics)
  │    Total Members · Active Members · Sales Revenue · Avg Utilisation
  │    Ad Spend · Net Profit · Avg Margin
  │
  └─ 7 Tabs:

Tab 1 👥 Membership
  ├─ Members by brand — grouped bar (Total vs Active)
  ├─ Membership type mix — donut
  ├─ New members vs Cancellations — area + dashed line
  ├─ NPS score distribution — bar coloured Detractor/Passive/Promoter
  ├─ Age group by brand — stacked bar
  └─ Gender split — donut

Tab 2 💰 Sales & Revenue
  ├─ Monthly revenue + 3-month rolling average — bar + line combo
  ├─ Revenue by brand — bar
  ├─ Revenue by product — horizontal bar (gradient)
  ├─ Revenue by channel — donut
  └─ Quarterly revenue by brand — stacked bar

Tab 3 🏋️ Capacity & Scheduling
  ├─ Avg utilisation by class vs 75% target — bar
  ├─ Utilisation heatmap Day of Week × Hour — imshow
  ├─ No-show rate by class — bar (green→red gradient)
  ├─ Monthly utilisation trend vs target — area
  └─ Peak hour utilisation by brand — multi-line

Tab 4 📣 Marketing Performance
  ├─ Spend vs Conversions by channel, bubble size = ROAS — scatter
  ├─ ROAS by channel vs average line — bar
  ├─ CPC / CPL / CPA by channel — grouped bar
  ├─ Monthly ad spend by brand — area
  └─ Full funnel: Impressions → Clicks → Leads → Conversions

Tab 5 📈 Profits
  ├─ P&L KPIs — Revenue / Costs / Net Profit / Margin
  ├─ Monthly Revenue vs Costs vs Net Profit — grouped bar + line
  ├─ Profit margin % trend by brand — multi-line
  ├─ Cost breakdown (9 categories) — donut
  ├─ Monthly cost stack by category — stacked bar
  ├─ Revenue vs Costs vs Profit by brand — grouped bar
  ├─ Avg profit margin % by brand — gradient bar
  ├─ Location P&L leaderboard — sortable data table
  └─ Quarterly EBITDA by brand — grouped bar

Tab 6 🤖 AI Insights
  ├─ [Button] Generate All Insights (5 parallel LLM calls)
  │    ├─ Membership insight box
  │    ├─ Sales insight box
  │    ├─ Capacity insight box
  │    ├─ Marketing insight box
  │    └─ Profits insight box
  └─ Executive Report — full narrative prose

Tab 7 🔮 AI Dashboard
  ├─ 12 suggested question chips (4-column grid, click to run instantly)
  ├─ Free-text input with Enter ➤ button + Clear button
  ├─ Multi-turn conversation (last 6 messages sent as context)
  └─ Per answer:
       ├─ User bubble (right-aligned)
       ├─ Assistant interpretation bubble
       ├─ Plotly chart (full width, auto-selected type)
       ├─ SQL query expander (collapsible)
       └─ Raw data table expander (collapsible)
```

---

## 💬 Sample Questions for the AI Dashboard

### Profitability
- `Which brand has the highest profit margin?`
- `Show me the top 5 most profitable locations`
- `What is the monthly net profit trend for Genesis Health + Fitness?`
- `Which location has the highest staff cost as a percentage of revenue?`
- `Compare EBITDA across all brands for 2024`
- `Which quarter had the best profit margin?`
- `Show me all locations with profit margin below 15%`

### Membership & Retention
- `What is the churn rate by membership type?`
- `How many members joined each month in 2024?`
- `Which brand has the most active members?`
- `What is the average NPS score per brand?`
- `Show me cancellations vs new sign-ups by month`
- `Which age group has the highest average membership fee?`
- `How many Family members cancelled in the last 12 months?`

### Sales & Revenue
- `What are the top 3 revenue-generating products?`
- `Which channel drives the most revenue?`
- `Show monthly revenue for Ninja Parc`
- `What was total revenue in Q3 2024?`
- `Which location generated the most sales?`
- `What is the average transaction value by product?`
- `Compare revenue between 2023 and 2024 by brand`

### Capacity & Scheduling
- `Which class has the worst no-show rate?`
- `What is the average utilisation by day of the week?`
- `Which hour of the day is busiest across all brands?`
- `Show me classes with utilisation below 60%`
- `Which brand has the best average class attendance?`
- `How many sessions were run per month in 2024?`
- `What is the average capacity booked for HIIT classes?`

### Marketing
- `Which marketing channel has the best ROAS?`
- `What is the cost per lead by channel?`
- `Which brand spends the most on marketing?`
- `Show me campaigns with ROAS above 3`
- `What is the total number of leads generated by Facebook?`
- `Which channel has the lowest cost per acquisition?`
- `Compare impressions vs conversions across all channels`

### Cross-domain / Advanced
- `Which locations have high ad spend but low revenue?`
- `List all locations sorted by profit descending`
- `What is the total revenue across all brands in 2024?`
- `Show me the month with the highest revenue and lowest costs`
- `Which brand has both high utilisation and high profit margin?`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Streamlit ≥ 1.35 |
| Charts | Plotly Express + Graph Objects |
| Data Processing | Pandas + NumPy |
| In-memory SQL Engine | DuckDB |
| LLM Client | OpenAI SDK (via OpenRouter) |
| LLM Model | `anthropic/claude-sonnet-4-5` |
| Parallel Execution | `concurrent.futures.ThreadPoolExecutor` |
| Theme | Slate dark — CSS variables, DM Sans + DM Serif Display |

---

## 📊 Synthetic Data Summary

| Dataset | Rows | Key Fields |
|---|---|---|
| membership | 5,000 | brand, type, join/cancel dates, NPS, monthly fee |
| sales | 8,000 | product, amount, channel, date, quarter |
| capacity | 3,000 | class, utilisation %, no-show rate, hour, day |
| marketing | 500 | channel, spend, ROAS, CPC, CPL, CPA, funnel |
| profits | ~1,152 | P&L per brand/location/month — 9 cost line items |

All data covers **January 2023 – December 2024** across **4 Belgravia brands** and **14 locations**.

---

## 🔑 Key Design Decisions

**Chip → query queue pattern**  
Streamlit reruns the entire script on every interaction. Chip buttons set `st.session_state.dash_queue` and call `st.rerun()`. The next rerun checks the queue at the very top before rendering anything, ensuring the question is processed cleanly without fighting the text input widget's own state.

**Parallel LLM calls**  
`ThreadPoolExecutor` fires all 5 domain insight calls simultaneously. Each thread makes an independent blocking HTTP request to OpenRouter. Total latency ≈ max(single call) rather than sum(all calls).

**DuckDB in-memory engine**  
All 5 DataFrames are registered as views in a fresh `duckdb.connect(":memory:")` connection per question. This means the LLM can write real SQL (JOINs, CTEs, window functions, date arithmetic) and it executes correctly — no custom query-builder logic required.

**Conversation context**  
The last 6 messages from `dash_history` are serialised and prepended to every LLM prompt, allowing follow-up questions like *"now break that down by location"* or *"filter to 2024 only"* to resolve correctly against prior results.
