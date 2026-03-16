"""
app.py
Belgravia Health & Fitness — Business Intelligence Platform
Light / Clean theme  |  Tabs: Membership · Sales · Capacity · Marketing · Profits · AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from generate_data import load_all
from ai_agent import get_parallel_insights, get_dashboard_spec, get_executive_report
from data_analyst import chat_turn

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Belgravia BI | Intelligence Platform",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS — Light / Clean theme ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

/* ── Slate theme: warm dark-grey, not black ── */
:root {
    --bg-base:    #1a1f2e;
    --bg-surface: #212736;
    --bg-raised:  #272d3d;
    --bg-hover:   #2e3548;
    --border:     #323b52;
    --border-soft:#2a3248;
    --text-primary:   #e8edf5;
    --text-secondary: #8b95a8;
    --text-muted:     #5a6478;
    --accent:     #4f8ef7;
    --accent-dim: #1e3a6e;
    --green:      #34d399;
    --red:        #f87171;
    --orange:     #fb923c;
    --purple:     #a78bfa;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg-base);
    color: var(--text-primary);
}
.stApp { background-color: var(--bg-base); }

/* Streamlit internal overrides */
[data-testid="stAppViewContainer"] { background-color: var(--bg-base); }
[data-testid="stHeader"] { background-color: var(--bg-base); }
[data-testid="stVerticalBlock"] { background-color: transparent; }
.main .block-container { background-color: transparent; }

section[data-testid="stSidebar"] {
    background: var(--bg-surface);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
section[data-testid="stSidebar"] .stCaption { color: var(--text-muted) !important; }

/* ── Metric cards ── */
.metric-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 10px;
    padding: 18px 20px;
    text-align: left;
    margin-bottom: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1rem;
    color: var(--text-primary);
    line-height: 1.1;
}
.metric-label {
    font-size: 0.76rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 5px;
}
.metric-delta { font-size: 0.8rem; color: var(--green); font-weight: 600; margin-top: 4px; }
.metric-delta.neg { color: var(--red); }

/* ── Section headers ── */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
}

/* ── Insight boxes ── */
.insight-box {
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.25);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.88rem;
    line-height: 1.75;
    color: #c5d5f0;
}
.insight-box.purple {
    background: rgba(167,139,250,0.08);
    border-color: rgba(167,139,250,0.25);
    border-left-color: var(--purple);
    color: #d4c8f8;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px 6px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 7px;
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 0.88rem;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #ffffff !important;
}

/* ── Form inputs ── */
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stTextInput"] label {
    color: var(--text-secondary) !important;
    font-size: 0.82rem;
    font-weight: 500;
}

.stTextInput > div > div > input {
    background: var(--bg-raised) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-raised) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
    transition: background 0.18s, transform 0.12s;
}
.stButton > button:hover {
    background: #3a7de8;
    transform: translateY(-1px);
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { background: var(--bg-surface) !important; border-radius: 8px; }
.stDataFrame th { background: var(--bg-raised) !important; color: var(--text-secondary) !important; }
.stDataFrame td { color: var(--text-primary) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--bg-surface);
    border: 1px solid var(--border) !important;
    border-radius: 8px;
}
[data-testid="stExpander"] summary { color: var(--text-secondary) !important; }

/* ── Alerts ── */
[data-testid="stAlert"] { background: var(--bg-raised) !important; border-color: var(--border) !important; }

/* ── Sidebar text ── */
.sidebar-brand { font-family: 'DM Serif Display', serif; font-size: 1.35rem; color: var(--text-primary); }
.sidebar-sub { font-size: 0.72rem; color: var(--text-muted); }

/* ── Hero ── */
.hero-title { font-family: 'DM Serif Display', serif; font-size: 2.2rem; color: var(--text-primary); line-height: 1.15; }
.hero-accent { color: var(--accent); }
.hero-sub { color: var(--text-secondary); font-size: 0.93rem; margin-top: 4px; }

hr { border-color: var(--border); }

/* ── Chat UI ── */
.chat-bubble {
    max-width: 85%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 0.9rem;
    line-height: 1.65;
    margin-bottom: 4px;
    word-wrap: break-word;
}
.chat-user {
    background: var(--accent);
    color: #ffffff;
    margin-left: auto;
    border-bottom-right-radius: 3px;
}
.chat-assistant {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    color: var(--text-primary);
    border-bottom-left-radius: 3px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.chat-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-bottom: 3px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.chat-label.user-label { text-align: right; color: var(--accent); }
.sql-block {
    background: var(--bg-raised);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    color: #94a8c8;
    margin-top: 8px;
    white-space: pre-wrap;
    word-break: break-all;
}
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 16px; }
.chip {
    background: var(--accent-dim);
    border: 1px solid rgba(79,142,247,0.35);
    color: #93bbf8;
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 0.78rem;
    cursor: pointer;
    white-space: nowrap;
}

</style>
""", unsafe_allow_html=True)

# ── Plotly light template ──────────────────────────────────────────────────────
COLORS = ["#2563eb", "#7c3aed", "#16a34a", "#ea580c", "#db2777", "#0891b2", "#ca8a04"]

def lyt(**overrides):
    base = dict(
        paper_bgcolor="#212736",
        plot_bgcolor="#1a1f2e",
        font=dict(color="#8b95a8", family="DM Sans"),
        title_font=dict(color="#e8edf5", family="DM Sans", size=14),
        xaxis=dict(gridcolor="#272d3d", linecolor="#323b52", zerolinecolor="#323b52",
                   tickfont=dict(color="#8b95a8")),
        yaxis=dict(gridcolor="#272d3d", linecolor="#323b52", zerolinecolor="#323b52",
                   tickfont=dict(color="#8b95a8")),
        legend=dict(bgcolor="#212736", bordercolor="#323b52", borderwidth=1,
                    font=dict(color="#8b95a8")),
        colorway=COLORS,
        margin=dict(t=40, l=10, r=10, b=10),
    )
    base.update(overrides)
    return base


# ── Helpers ────────────────────────────────────────────────────────────────────
def metric_card(label, value, delta=None, neg=False):
    delta_cls = "neg" if neg else ""
    arrow = "▼" if neg else "▲"
    delta_html = f'<div class="metric-delta {delta_cls}">{arrow} {delta}</div>' if delta else ""
    return f"""<div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>"""

def section_header(text):
    st.html(f'<div class="section-header">{text}</div>')

def insight_box(text, style=""):
    st.html(f'<div class="insight-box {style}">{text}</div>')

def apply_brand_filter(df, brands):
    return df[df["brand"].isin(brands)] if brands else df


# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading Belgravia data warehouse…")
def load_data():
    return load_all()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html("""<div style="padding:18px 0 12px">
        <div class="sidebar-brand">💪 Belgravia BI</div>
        <div class="sidebar-sub">Intelligence Platform · v2.0</div>
    </div>""")
    st.markdown("---")

    st.markdown("**🏢 Brand Filter**")
    ALL_BRANDS = ["Genesis Health + Fitness", "Ninja Parc", "Jump Swim Schools", "Belgravia Kids Swim"]
    selected_brands = st.multiselect("Brands", ALL_BRANDS, default=ALL_BRANDS, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**📅 Year**")
    year_filter = st.selectbox("Year", ["All", "2023", "2024"], index=0, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**🤖 AI Settings**")
    api_key = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-...",
                            help="Get a free key at openrouter.ai")
    ai_enabled = bool(api_key)
    if ai_enabled:
        st.success("✅ AI features active")
    else:
        st.caption("🔑 Add key to unlock AI tabs")

    st.markdown("---")
    st.caption("Built for Belgravia Health & Fitness\nBI Analyst Demo · 2024")


# ── Load & filter ──────────────────────────────────────────────────────────────
raw      = load_data()
mem_df   = apply_brand_filter(raw["membership"].copy(), selected_brands)
sales_df = apply_brand_filter(raw["sales"].copy(), selected_brands)
cap_df   = apply_brand_filter(raw["capacity"].copy(), selected_brands)
mkt_df   = apply_brand_filter(raw["marketing"].copy(), selected_brands)
pnl_df   = apply_brand_filter(raw["profits"].copy(), selected_brands)

if year_filter != "All":
    y = year_filter
    mem_df   = mem_df[pd.to_datetime(mem_df["join_date"]).dt.year == int(y)]
    sales_df = sales_df[pd.to_datetime(sales_df["sale_date"]).dt.year == int(y)]
    cap_df   = cap_df[pd.to_datetime(cap_df["date"]).dt.year == int(y)]
    mkt_df   = mkt_df[mkt_df["month"].str.startswith(y)]
    pnl_df   = pnl_df[pnl_df["month"].str.startswith(y)]


# ── Hero ───────────────────────────────────────────────────────────────────────
st.html("""<div style="padding:16px 0 8px">
  <div class="hero-title">Belgravia <span class="hero-accent">Health &amp; Fitness</span></div>
  <div class="hero-sub">Business Intelligence Platform · Membership · Sales · Capacity · Marketing · Profits</div>
</div>""")

# ── KPI strip ──────────────────────────────────────────────────────────────────
total_members  = len(mem_df)
active_members = int(mem_df["active"].sum())
total_revenue  = sales_df["amount"].sum()
avg_util       = cap_df["utilisation_pct"].mean()
total_spend    = mkt_df["spend"].sum()
net_profit     = pnl_df["gross_profit"].sum()
avg_margin     = pnl_df["profit_margin_pct"].mean()
total_rev_pnl  = pnl_df["total_revenue"].sum()
total_cost_pnl = pnl_df["total_costs"].sum()
total_ebitda   = pnl_df["ebitda"].sum()

c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
for col, lbl, val, d, neg in [
    (c1, "Total Members",   f"{total_members:,}",    "+12%",  False),
    (c2, "Active Members",  f"{active_members:,}",   None,    False),
    (c3, "Sales Revenue",   f"${total_revenue:,.0f}","8% YoY",False),
    (c4, "Avg Utilisation", f"{avg_util:.1f}%",      None,    False),
    (c5, "Ad Spend",        f"${total_spend:,.0f}",  None,    False),
    (c6, "Net Profit",      f"${net_profit:,.0f}",   None,    net_profit < 0),
    (c7, "Avg Margin",      f"{avg_margin:.1f}%",    None,    avg_margin < 10),
]:
    with col:
        st.html(metric_card(lbl, val, d, neg))

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "👥 Membership",
    "💰 Sales & Revenue",
    "🏋️ Capacity",
    "📣 Marketing",
    "📈 Profits",
    "🤖 AI Insights",
    "🔮 AI Dashboard",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MEMBERSHIP & RETENTION
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    section_header("Membership Overview")
    c1, c2 = st.columns(2)
    with c1:
        bc = mem_df.groupby("brand").agg(total=("member_id","count"), active=("active","sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Total",  x=bc["brand"], y=bc["total"],  marker_color=COLORS[0]))
        fig.add_trace(go.Bar(name="Active", x=bc["brand"], y=bc["active"], marker_color=COLORS[2]))
        fig.update_layout(title="Members by Brand", barmode="group", **lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        tc = mem_df["membership_type"].value_counts().reset_index()
        tc.columns = ["type","count"]
        fig = px.pie(tc, names="type", values="count", title="Membership Type Mix",
                     color_discrete_sequence=COLORS, hole=0.42)
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Retention & Churn")
    c1, c2 = st.columns(2)
    with c1:
        mem_df["join_month"] = pd.to_datetime(mem_df["join_date"]).dt.to_period("M").astype(str)
        mj = mem_df.groupby("join_month")["member_id"].count().reset_index()
        mj.columns = ["month","new"]
        mj = mj.sort_values("month").tail(24)
        cx = mem_df[mem_df["cancel_date"].notna()].copy()
        cx["cancel_month"] = pd.to_datetime(cx["cancel_date"]).dt.to_period("M").astype(str)
        mc = cx.groupby("cancel_month")["member_id"].count().reset_index()
        mc.columns = ["month","cancelled"]
        mg = pd.merge(mj, mc, on="month", how="left").fillna(0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mg["month"], y=mg["new"], name="New Members",
                                 line=dict(color=COLORS[2], width=2.5),
                                 fill="tozeroy", fillcolor="rgba(22,163,74,0.08)"))
        fig.add_trace(go.Scatter(x=mg["month"], y=mg["cancelled"], name="Cancellations",
                                 line=dict(color="#dc2626", width=2, dash="dot")))
        fig.update_layout(title="New Members vs Cancellations", **lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        nd = mem_df["nps_score"].value_counts().sort_index().reset_index()
        nd.columns = ["score","count"]
        nd["cat"] = nd["score"].apply(lambda x: "Detractor" if x<=6 else ("Passive" if x<=8 else "Promoter"))
        fig = px.bar(nd, x="score", y="count", color="cat", title="NPS Score Distribution",
                     color_discrete_map={"Detractor":"#dc2626","Passive":"#ea580c","Promoter":"#16a34a"})
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Demographics")
    c1, c2 = st.columns(2)
    with c1:
        ag = mem_df.groupby(["brand","age_group"])["member_id"].count().reset_index()
        ag.columns = ["brand","age_group","count"]
        fig = px.bar(ag, x="age_group", y="count", color="brand", title="Age Group by Brand",
                     barmode="stack", color_discrete_sequence=COLORS)
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        gc = mem_df["gender"].value_counts().reset_index()
        gc.columns = ["gender","count"]
        fig = px.pie(gc, names="gender", values="count", title="Gender Split",
                     color_discrete_sequence=COLORS, hole=0.45)
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SALES & REVENUE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    section_header("Revenue Performance")
    c1, c2 = st.columns(2)
    with c1:
        mr = sales_df.groupby("month")["amount"].sum().reset_index().sort_values("month")
        mr["rolling"] = mr["amount"].rolling(3).mean()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mr["month"], y=mr["amount"], name="Revenue", marker_color="#1e3a6e"))
        fig.add_trace(go.Scatter(x=mr["month"], y=mr["rolling"], name="3M Avg",
                                 line=dict(color=COLORS[0], width=2.5)))
        fig.update_layout(title="Monthly Revenue + 3M Rolling Avg", **lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        rb = sales_df.groupby("brand")["amount"].sum().reset_index()
        fig = px.bar(rb, x="brand", y="amount", title="Revenue by Brand",
                     color="brand", color_discrete_sequence=COLORS)
        fig.update_layout(showlegend=False, **lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Product & Channel Mix")
    c1, c2 = st.columns(2)
    with c1:
        pr = sales_df.groupby("product")["amount"].sum().sort_values().reset_index()
        fig = px.bar(pr, x="amount", y="product", orientation="h", title="Revenue by Product",
                     color="amount", color_continuous_scale=["#1e3a6e","#4f8ef7"])
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        cr = sales_df.groupby("channel")["amount"].sum().reset_index()
        fig = px.pie(cr, names="channel", values="amount", title="Revenue by Channel",
                     color_discrete_sequence=COLORS, hole=0.4)
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Quarterly Breakdown")
    qr = sales_df.groupby(["quarter","brand"])["amount"].sum().reset_index()
    fig = px.bar(qr, x="quarter", y="amount", color="brand", title="Quarterly Revenue by Brand",
                 barmode="stack", color_discrete_sequence=COLORS)
    fig.update_layout(**lyt())
    st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CAPACITY & SCHEDULING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    section_header("Utilisation Analysis")
    c1, c2 = st.columns(2)
    with c1:
        cu = cap_df.groupby("class")["utilisation_pct"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(cu, x="class", y="utilisation_pct", title="Avg Utilisation by Class (%)",
                     color="utilisation_pct", color_continuous_scale=["#1e3a6e","#4f8ef7"])
        fig.add_hline(y=75, line_dash="dot", line_color="#dc2626", annotation_text="75% Target")
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        heat = cap_df.groupby(["day_of_week","hour"])["utilisation_pct"].mean().reset_index()
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        hp = heat.pivot(index="day_of_week", columns="hour", values="utilisation_pct")
        hp = hp.reindex([d for d in day_order if d in hp.index])
        fig = px.imshow(hp, title="Utilisation Heatmap (Day × Hour)",
                        color_continuous_scale=["#0f172a","#1e3a6e","#4f8ef7"], aspect="auto")
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("No-Show & Attendance")
    c1, c2 = st.columns(2)
    with c1:
        ns = cap_df.groupby("class")["no_show_rate"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(ns, x="class", y="no_show_rate", title="Avg No-Show Rate by Class (%)",
                     color="no_show_rate", color_continuous_scale=["#14532d","#dc2626"])
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        mu = cap_df.groupby("month")["utilisation_pct"].mean().reset_index().sort_values("month")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mu["month"], y=mu["utilisation_pct"], name="Utilisation",
                                 line=dict(color=COLORS[1], width=2.5),
                                 fill="tozeroy", fillcolor="rgba(124,58,237,0.07)"))
        fig.add_hline(y=75, line_dash="dot", line_color="#16a34a", annotation_text="Target")
        fig.update_layout(title="Monthly Utilisation Trend", **lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Peak Hour by Brand")
    hb = cap_df.groupby(["hour","brand"])["utilisation_pct"].mean().reset_index()
    fig = px.line(hb, x="hour", y="utilisation_pct", color="brand",
                  title="Utilisation by Hour & Brand", color_discrete_sequence=COLORS, markers=True)
    fig.update_layout(**lyt())
    st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — MARKETING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    section_header("Campaign Performance")
    c1, c2 = st.columns(2)
    with c1:
        cp = mkt_df.groupby("channel").agg(
            spend=("spend","sum"), conversions=("conversions","sum"),
            leads=("leads","sum"), roas=("roas","mean")).reset_index()
        fig = px.scatter(cp, x="spend", y="conversions", size="roas", color="channel",
                         title="Spend vs Conversions (bubble = ROAS)",
                         color_discrete_sequence=COLORS, size_max=45)
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        fig = px.bar(cp.sort_values("roas", ascending=False),
                     x="channel", y="roas", title="ROAS by Channel",
                     color="roas", color_continuous_scale=["#1e3a6e","#4f8ef7"])
        fig.add_hline(y=cp["roas"].mean(), line_dash="dot", line_color="#dc2626",
                      annotation_text="Avg ROAS")
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Cost Efficiency")
    c1, c2 = st.columns(2)
    with c1:
        cm = mkt_df.groupby("channel").agg(cpl=("cpl","mean"), cpa=("cpa","mean"), cpc=("cpc","mean")).reset_index()
        fig = go.Figure()
        for i, m in enumerate(["cpl","cpa","cpc"]):
            fig.add_trace(go.Bar(name=m.upper(), x=cm["channel"], y=cm[m], marker_color=COLORS[i]))
        fig.update_layout(title="CPC / CPL / CPA by Channel", barmode="group", **lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        ms = mkt_df.groupby(["month","brand"])["spend"].sum().reset_index().sort_values("month")
        fig = px.area(ms, x="month", y="spend", color="brand", title="Monthly Ad Spend by Brand",
                      color_discrete_sequence=COLORS)
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Conversion Funnel")
    fd = mkt_df[["impressions","clicks","leads","conversions"]].sum()
    fig = go.Figure(go.Funnel(
        y=["Impressions","Clicks","Leads","Conversions"],
        x=fd.values, textinfo="value+percent initial",
        marker=dict(color=COLORS[:4])
    ))
    fig.update_layout(title="Full Marketing Funnel", **lyt())
    st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PROFITS  ← NEW
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    section_header("P&L Summary")

    overall_margin = net_profit / max(total_rev_pnl, 1) * 100
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1: st.html(metric_card("Total Revenue",  f"${total_rev_pnl:,.0f}"))
    with pc2: st.html(metric_card("Total Costs",    f"${total_cost_pnl:,.0f}"))
    with pc3: st.html(metric_card("Net Profit",     f"${net_profit:,.0f}",  neg=net_profit<0))
    with pc4: st.html(metric_card("Overall Margin", f"{overall_margin:.1f}%", neg=overall_margin<10))

    st.markdown("&nbsp;")
    c1, c2 = st.columns(2)
    with c1:
        mp = pnl_df.groupby("month").agg(
            revenue=("total_revenue","sum"),
            costs=("total_costs","sum"),
            profit=("gross_profit","sum")
        ).reset_index().sort_values("month")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mp["month"], y=mp["revenue"], name="Revenue", marker_color="#1e3a6e"))
        fig.add_trace(go.Bar(x=mp["month"], y=mp["costs"],   name="Costs",   marker_color="#4c1414"))
        fig.add_trace(go.Scatter(x=mp["month"], y=mp["profit"], name="Net Profit",
                                 line=dict(color=COLORS[2], width=2.5), mode="lines+markers"))
        fig.update_layout(title="Monthly Revenue vs Costs vs Net Profit", barmode="group", **lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        bm = pnl_df.groupby(["month","brand"])["profit_margin_pct"].mean().reset_index().sort_values("month")
        fig = px.line(bm, x="month", y="profit_margin_pct", color="brand",
                      title="Profit Margin % by Brand", color_discrete_sequence=COLORS)
        fig.add_hline(y=20, line_dash="dot", line_color="#6b7280", annotation_text="20% target")
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Cost Structure Breakdown")
    c1, c2 = st.columns(2)
    cost_cols   = ["cost_staff","cost_lease","cost_utilities","cost_equipment",
                   "cost_insurance","cost_marketing","cost_maintenance","cost_admin","cost_instructor"]
    cost_labels = ["Staff","Lease","Utilities","Equipment","Insurance",
                   "Marketing","Maintenance","Admin","Instructor"]
    with c1:
        cost_totals = [pnl_df[c].sum() for c in cost_cols]
        cpie = pd.DataFrame({"category": cost_labels, "amount": cost_totals})
        fig = px.pie(cpie, names="category", values="amount",
                     title="Cost Breakdown (All Brands)", color_discrete_sequence=COLORS, hole=0.45)
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        mc2 = pnl_df.groupby("month")[cost_cols].sum().reset_index().sort_values("month")
        fig = go.Figure()
        for i, (col, lbl) in enumerate(zip(cost_cols, cost_labels)):
            fig.add_trace(go.Bar(name=lbl, x=mc2["month"], y=mc2[col],
                                 marker_color=COLORS[i % len(COLORS)]))
        fig.update_layout(title="Monthly Cost Stack", barmode="stack", **lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Brand Profitability")
    c1, c2 = st.columns(2)
    with c1:
        bp = pnl_df.groupby("brand").agg(
            revenue=("total_revenue","sum"),
            costs=("total_costs","sum"),
            profit=("gross_profit","sum"),
            margin=("profit_margin_pct","mean")
        ).reset_index().sort_values("profit", ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=bp["brand"], y=bp["revenue"], name="Revenue", marker_color="#1e3a6e"))
        fig.add_trace(go.Bar(x=bp["brand"], y=bp["costs"],   name="Costs",   marker_color="#4c1414"))
        fig.add_trace(go.Bar(x=bp["brand"], y=bp["profit"],  name="Profit",  marker_color="#14532d"))
        fig.update_layout(title="Revenue vs Costs vs Profit by Brand", barmode="group", **lyt())
        st.plotly_chart(fig, width='stretch')
    with c2:
        fig = px.bar(bp, x="brand", y="margin", title="Avg Profit Margin % by Brand",
                     color="margin", color_continuous_scale=["#7f1d1d","#713f12","#14532d"])
        fig.add_hline(y=20, line_dash="dot", line_color="#6b7280", annotation_text="Target 20%")
        fig.update_layout(**lyt())
        st.plotly_chart(fig, width='stretch')

    section_header("Location P&L Leaderboard")
    loc_p = pnl_df.groupby(["brand","location"]).agg(
        revenue=("total_revenue","sum"),
        costs=("total_costs","sum"),
        profit=("gross_profit","sum"),
        margin=("profit_margin_pct","mean")
    ).reset_index().sort_values("profit", ascending=False).copy()
    loc_p["revenue"] = loc_p["revenue"].map("${:,.0f}".format)
    loc_p["costs"]   = loc_p["costs"].map("${:,.0f}".format)
    loc_p["profit"]  = loc_p["profit"].map("${:,.0f}".format)
    loc_p["margin"]  = loc_p["margin"].map("{:.1f}%".format)
    st.dataframe(loc_p.rename(columns={
        "brand":"Brand","location":"Location","revenue":"Revenue",
        "costs":"Total Costs","profit":"Net Profit","margin":"Margin %"
    }), width='stretch', hide_index=True)

    section_header("Quarterly EBITDA")
    qe = pnl_df.groupby(["quarter","brand"])["ebitda"].sum().reset_index()
    fig = px.bar(qe, x="quarter", y="ebitda", color="brand",
                 title="Quarterly EBITDA by Brand", barmode="group", color_discrete_sequence=COLORS)
    fig.update_layout(**lyt())
    st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — AI INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.html("""<div class="hero-sub" style="margin-bottom:16px;">
    Parallel LLM analysis fires 5 domain calls simultaneously via <code>ThreadPoolExecutor</code>.
    Typically 4–6 seconds instead of 20+ seconds sequential.
    </div>""")

    if not ai_enabled:
        st.warning("🔑 Enter your OpenRouter API key in the sidebar to enable AI insights.")
    else:
        if st.button("⚡ Generate All Insights (Parallel)", width='stretch'):
            active_rate = active_members / max(total_members, 1) * 100
            churn       = mem_df["cancel_date"].notna().sum() / max(total_members, 1) * 100
            top_product = sales_df.groupby("product")["amount"].sum().idxmax()
            best_roas   = mkt_df.groupby("channel")["roas"].mean().idxmax()
            low_cls     = cap_df.groupby("class")["utilisation_pct"].mean().idxmin()
            best_brand  = pnl_df.groupby("brand")["profit_margin_pct"].mean().idxmax()
            overall_margin = net_profit / max(total_rev_pnl, 1) * 100

            kpi_blocks = {
                "👥 Membership & Retention": f"""
                  Total: {total_members:,} | Active: {active_members:,} ({active_rate:.1f}%)
                  Churn rate: {churn:.1f}% | Avg NPS: {mem_df['nps_score'].mean():.1f}/10
                  Top type: {mem_df['membership_type'].value_counts().idxmax()}
                """,
                "💰 Sales & Revenue": f"""
                  Total revenue: ${total_revenue:,.0f}
                  Top product: {top_product} | Avg transaction: ${sales_df['amount'].mean():.2f}
                """,
                "🏋️ Capacity & Scheduling": f"""
                  Avg utilisation: {avg_util:.1f}% (target 75%)
                  Lowest class: {low_cls} | No-show: {cap_df['no_show_rate'].mean():.1f}%
                """,
                "📣 Marketing": f"""
                  Ad spend: ${total_spend:,.0f} | Best ROAS: {best_roas}
                  Conversion rate: {mkt_df['conversions'].sum()/max(mkt_df['leads'].sum(),1)*100:.1f}%
                """,
                "📈 Profits": f"""
                  Revenue: ${total_rev_pnl:,.0f} | Costs: ${total_cost_pnl:,.0f}
                  Net profit: ${net_profit:,.0f} | Margin: {overall_margin:.1f}%
                  Best brand: {best_brand} | EBITDA: ${total_ebitda:,.0f}
                """,
            }

            with st.spinner("Running 5-way parallel AI analysis…"):
                insights = get_parallel_insights(api_key, kpi_blocks)

            for sect, text in insights.items():
                section_header(sect)
                insight_box(text.replace("\n", "<br>"))

            st.markdown("---")
            section_header("📋 Executive Report")
            combined = "\n\n".join(f"**{k}**\n{v}" for k, v in kpi_blocks.items())
            with st.spinner("Generating executive report…"):
                report = get_executive_report(api_key, combined)
            insight_box(report.replace("\n", "<br>"), style="purple")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — AI DASHBOARD  (unified chat + NL→SQL→DuckDB→Chart)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:

    if not ai_enabled:
        st.warning("🔑 Enter your OpenRouter API key in the sidebar to use the AI Dashboard.")
    else:
        # ── Session state ──────────────────────────────────────────────────────
        if "dash_history" not in st.session_state:
            st.session_state.dash_history = []
        # dash_queue: question waiting to be processed this rerun
        if "dash_queue" not in st.session_state:
            st.session_state.dash_queue = ""

        # ── DataFrames for DuckDB (defined early, used by both chip + send paths)
        analyst_dfs = {
            "membership": raw["membership"],
            "sales":      raw["sales"],
            "capacity":   raw["capacity"],
            "marketing":  raw["marketing"],
            "profits":    raw["profits"],
        }

        def run_question(q):
            """Add question to history, call LLM+DuckDB, store result, rerun."""
            q = q.strip()
            if not q:
                return
            st.session_state.dash_history.append({"role": "user", "content": q})
            history_ctx = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.dash_history[:-1]
            ]
            with st.spinner("Writing SQL, querying data, building chart…"):
                result = chat_turn(api_key, q, analyst_dfs, history_ctx)
            st.session_state.dash_history.append({
                "role":       "assistant",
                "content":    result["interpretation"] if not result["error"] else f"❌ {result['error']}",
                "sql":        result["sql"],
                "data":       result["data"],
                "chart_spec": result["chart_spec"],
                "row_count":  result.get("row_count", 0),
                "error":      result["error"],
            })
            st.session_state.dash_queue = ""
            st.rerun()

        # ── Process any queued question from PREVIOUS rerun (chip click) ───────
        if st.session_state.dash_queue:
            run_question(st.session_state.dash_queue)

        # ── Suggested question chips ───────────────────────────────────────────
        SUGGESTIONS = [
            "Which brand has the highest profit margin?",
            "Show monthly revenue trend for 2024",
            "Top 5 locations by net profit",
            "Which class has the worst no-show rate?",
            "Compare ROAS across all marketing channels",
            "What is the churn rate by membership type?",
            "Which quarter had the most new members?",
            "Show average utilisation by day of week",
            "What are the top 3 products by revenue?",
            "Which location spends the most on staff costs?",
            "Compare revenue vs costs by brand",
            "Locations with profit margin below 15%",
        ]

        st.html("""<div style="font-size:0.78rem; color:var(--text-muted);
                   text-transform:uppercase; letter-spacing:0.07em;
                   margin-bottom:8px; font-weight:600;">💡 Suggested questions</div>""")

        chip_cols = st.columns(4)
        for idx, sug in enumerate(SUGGESTIONS):
            with chip_cols[idx % 4]:
                if st.button(sug, key=f"chip_{idx}"):
                    # Queue the question — will be picked up at top of next rerun
                    st.session_state.dash_queue = sug
                    st.rerun()

        st.markdown('<hr style="border-color:var(--border); margin:14px 0 10px;">', unsafe_allow_html=True)

        # ── Manual input bar ───────────────────────────────────────────────────
        col_inp, col_send, col_clear = st.columns([8, 1, 1])
        with col_inp:
            user_input = st.text_input(
                "question",
                placeholder="Ask anything — e.g. Show revenue trend by brand for 2024",
                label_visibility="collapsed",
                key="dash_input",
            )
        with col_send:
            send_clicked = st.button("Enter ➤", key="dash_send")
        with col_clear:
            if st.button("Clear", key="dash_clear"):
                st.session_state.dash_history = []
                st.session_state.dash_queue = ""
                st.rerun()

        # ── Handle manual send ─────────────────────────────────────────────────
        if send_clicked and user_input.strip():
            run_question(user_input)

        # ── Render conversation ────────────────────────────────────────────────
        if not st.session_state.dash_history:
            st.html("""
            <div style="text-align:center; padding:56px 0 32px;">
                <div style="font-size:3rem; margin-bottom:14px;">🔮</div>
                <div style="font-family:'DM Serif Display',serif; font-size:1.4rem;
                            color:var(--text-primary); margin-bottom:8px;">
                    Ask anything about your data
                </div>
                <div style="font-size:0.9rem; color:var(--text-muted); max-width:480px; margin:0 auto;">
                    Type a question above or pick one of the suggestions.
                    The AI writes SQL, runs it on DuckDB, interprets the result,
                    and renders a chart automatically.
                </div>
            </div>
            """)
        else:
            # Show newest first — reverse list but keep index for chart keys
            for i, msg in enumerate(st.session_state.dash_history):
                if msg["role"] == "user":
                    st.html(f"""
                    <div style="display:flex; justify-content:flex-end; margin:8px 0 4px;">
                        <div class="chat-bubble chat-user">{msg['content']}</div>
                    </div>""")
                else:
                    # ── Assistant turn ─────────────────────────────────────────
                    # Interpretation bubble
                    st.html(f"""
                    <div class="chat-bubble chat-assistant" style="margin:4px 0 10px;">
                        {msg['content'].replace(chr(10), '<br>')}
                    </div>""")

                    # Chart — full width, rendered prominently
                    if msg.get("chart_spec") and msg.get("data") is not None and len(msg["data"]) > 0:
                        df_r = msg["data"]
                        cs   = msg["chart_spec"]
                        x    = cs.get("x_col")
                        y    = cs.get("y_col")
                        clr  = cs.get("color_col")
                        ctype = cs.get("chart_type", "bar")
                        # Use the preceding user message as fallback title
                        prev_user = next(
                            (m["content"] for m in reversed(st.session_state.dash_history[:i])
                             if m["role"] == "user"), ""
                        )
                        title = cs.get("chart_title") or prev_user or ""

                        if x and y and x in df_r.columns and y in df_r.columns:
                            try:
                                clr_arg = clr if clr and clr in df_r.columns else None
                                if ctype == "line":
                                    fig = px.line(df_r, x=x, y=y, color=clr_arg,
                                                  color_discrete_sequence=COLORS, markers=True)
                                elif ctype == "pie":
                                    fig = px.pie(df_r, names=x, values=y,
                                                 color_discrete_sequence=COLORS, hole=0.42)
                                elif ctype == "scatter":
                                    fig = px.scatter(df_r, x=x, y=y, color=clr_arg,
                                                     color_discrete_sequence=COLORS, size_max=30)
                                elif ctype == "area":
                                    fig = px.area(df_r, x=x, y=y, color=clr_arg,
                                                  color_discrete_sequence=COLORS)
                                else:
                                    fig = px.bar(df_r, x=x, y=y, color=clr_arg,
                                                 color_discrete_sequence=COLORS)
                                fig.update_layout(title=title, **lyt())
                                st.plotly_chart(fig, width='stretch', key=f"dash_chart_{i}")
                            except Exception as ce:
                                st.caption(f"Chart render issue: {ce}")

                    # Two-column detail: SQL  |  Data table
                    if msg.get("sql") or (msg.get("data") is not None and len(msg.get("data", [])) > 0):
                        dc1, dc2 = st.columns(2)
                        with dc1:
                            if msg.get("sql"):
                                with st.expander(f"🔍 SQL  ·  {msg.get('row_count',0)} rows returned", expanded=False):
                                    st.code(msg["sql"], language="sql")
                        with dc2:
                            if msg.get("data") is not None and len(msg["data"]) > 0:
                                with st.expander(f"📊 Data table  ·  {len(msg['data'])} rows", expanded=False):
                                    st.dataframe(msg["data"], width='stretch', hide_index=True)

                    st.html('<div style="border-top:1px solid var(--border); margin:16px 0;">')
