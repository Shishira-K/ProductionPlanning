import streamlit as st


# --------------------------------------------------------
# Load Custom CSS
# --------------------------------------------------------

def load_css():

    st.markdown("""
    <style>

    /* ============================
       Main Page
    ============================ */

    .main {
        background-color: #F6F8FC;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* ============================
       Fonts
    ============================ */

    html,
    body,
    [class*="css"] {
        font-family: "Segoe UI", sans-serif;
    }

    h1{
        color:#0F172A !important;
        font-weight:700;
    }

    h2,h3,h4,h5,h6{
        color:#1E293B !important;
        font-weight:600;
    }

    p, li, label, span{
        color:#334155 !important;
    }

    /* ============================
       Sidebar
    ============================ */

    section[data-testid="stSidebar"]{
        background:#1E1E2F;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span{
        color:white !important;
    }

    section[data-testid="stSidebar"] .stMarkdown{
        color:white !important;
    }

    /* ============================
       Sidebar Expanders
    ============================ */

    section[data-testid="stSidebar"] details{

        background:#2A2D3E;

        border-radius:10px;

        border:1px solid #3D4158;

        margin-bottom:10px;

        padding:4px;

    }

    section[data-testid="stSidebar"] summary{

        color:white !important;

        font-weight:600;

    }

    /* ============================
       Metric Cards
    ============================ */

    div[data-testid="metric-container"]{

        background:white;

        border-radius:14px;

        padding:18px;

        box-shadow:0 4px 12px rgba(0,0,0,0.08);

        border:1px solid #E2E8F0;

    }

    div[data-testid="metric-container"] label{

        color:#64748B !important;

        font-size:14px;

        font-weight:600;

    }

    div[data-testid="metric-container"] div{

        color:#0F172A !important;

    }

    /* ============================
       Buttons
    ============================ */

    .stButton>button{

        width:100%;

        border-radius:10px;

        height:45px;

        background:#2563EB;

        color:white;

        border:none;

        font-weight:600;

    }

    .stButton>button:hover{

        background:#1D4ED8;

        color:white;

    }

    /* ============================
       Data Editor
    ============================ */

    div[data-testid="stDataEditor"]{

        border-radius:12px;

        overflow:hidden;

        border:1px solid #E2E8F0;

    }

    /* ============================
       Tabs
    ============================ */

    button[data-baseweb="tab"]{

        font-weight:600;

        font-size:15px;

    }

    /* ============================
       Info Box
    ============================ */

    div[data-testid="stAlert"]{

        border-radius:12px;

    }

    </style>
    """, unsafe_allow_html=True)


# --------------------------------------------------------
# Page Header
# --------------------------------------------------------

def header():

    st.title("🏭 Production Planning Optimization Dashboard")

    st.caption(
        "Mixed Integer Linear Programming (MILP) Decision Support Tool"
    )


# --------------------------------------------------------
# Sidebar Title
# --------------------------------------------------------

def sidebar_title():

    st.sidebar.title("⚙️ Model Inputs")


# --------------------------------------------------------
# Overview Section
# --------------------------------------------------------

def show_overview(months, demand):

    left, right = st.columns([2.4, 1])

    with left:

        st.subheader("Problem Overview")

        st.markdown("""
This application solves a **multi-period production planning problem**
using **Mixed Integer Linear Programming (MILP).**

The optimizer determines:

- 📦 Monthly Production
- 📊 Inventory Levels
- 🏭 Shift Selection
- 🔄 Switching Decisions

while minimizing the **overall production cost**.
""")

    with right:

        st.markdown(f"""
<div style="
background:#EAF3FF;
padding:22px;
border-radius:14px;
border-left:6px solid #2563EB;
box-shadow:0 3px 10px rgba(0,0,0,.08);
">

<h3 style="margin-top:0;color:#0F172A;">
📋 Planning Summary
</h3>

<p style="margin-bottom:5px;color:#2563EB;font-weight:600;">
Planning Horizon
</p>

<h2 style="margin-top:0;color:#111827;">
{months} Months
</h2>

<hr>

<p style="margin-bottom:5px;color:#2563EB;font-weight:600;">
Total Demand
</p>

<h2 style="margin-top:0;color:#111827;">
{sum(demand):,}
</h2>

<p style="color:#64748B;">
Units
</p>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------
# KPI Cards
# --------------------------------------------------------

def show_metrics(summary, results):

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Cost",
        f"£{summary['Total Cost']:,.0f}"
    )

    c2.metric(
        "Production",
        f"{summary['Total Production']:,.0f}"
    )

    c3.metric(
        "Average Inventory",
        f"{summary['Average Inventory']:,.0f}"
    )

    c4.metric(
        "Extended Shift",
        summary["Extended Months"]
    )

    st.markdown("")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Normal Shift",
        summary["Normal Months"]
    )

    c6.metric(
        "Idle Months",
        summary["Idle Months"]
    )

    c7.metric(
        "Solver Time",
        f"{results['solver_time']} s"
    )

    c8.metric(
        "Variables",
        results["num_variables"]
    )


# --------------------------------------------------------
# Constraint Status
# --------------------------------------------------------

def constraint_status(title, passed):

    if passed:

        st.success(f"✔ {title}")

    else:

        st.error(f"✖ {title}")


# --------------------------------------------------------
# Insights Box
# --------------------------------------------------------

def insight(text):

    st.info(text)


# --------------------------------------------------------
# Section Divider
# --------------------------------------------------------

def divider():

    st.markdown("---")


# --------------------------------------------------------
# Footer
# --------------------------------------------------------

def footer():

    st.markdown("---")

    st.caption(
        "Production Planning Optimization Dashboard | Built with Streamlit, PuLP & Plotly"
    )
