import streamlit as st
import pandas as pd
import copy

from config import BASE_CASE
from optimizer import solve_model

import ui
import charts
import insights
import exports


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Production Planning Optimizer",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

ui.load_css()
ui.header()

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "params" not in st.session_state:
    st.session_state.params = copy.deepcopy(BASE_CASE)

if "results" not in st.session_state:
    st.session_state.results = None

params = st.session_state.params

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

ui.sidebar_title()

if st.sidebar.button("🔄 Load Base Case"):

    st.session_state.params = BASE_CASE.copy()
    params = st.session_state.params

# ---------------------------------------------------------
# Planning Horizon
# ---------------------------------------------------------

with st.sidebar.expander("Planning Horizon", expanded=True):

    months = st.number_input(

        "Number of Months",

        min_value=1,

        max_value=36,

        value=params["months"],

        step=1

    )

# ---------------------------------------------------------
# Resize Demand List
# ---------------------------------------------------------

old = params["demand"]

if months > len(old):

    old.extend(

        [old[-1]] *

        (months - len(old))

    )

elif months < len(old):

    old = old[:months]

params["months"] = months
params["demand"] = old

# ---------------------------------------------------------
# Demand Table
# ---------------------------------------------------------

st.sidebar.markdown("### Monthly Demand")

demand_df = pd.DataFrame({

    "Month": range(1, months + 1),

    "Demand": params["demand"]

})

edited = st.sidebar.data_editor(

    demand_df,

    hide_index=True,

    use_container_width=True,

    key="DemandEditor"

)

params["demand"] = edited["Demand"].tolist()

# ---------------------------------------------------------
# Shift Parameters
# ---------------------------------------------------------

with st.sidebar.expander("Shift Parameters"):

    st.markdown("#### Normal Shift")

    params["shifts"]["Normal"]["capacity"] = st.number_input(

        "Normal Capacity",

        value=params["shifts"]["Normal"]["capacity"],

        step=100

    )

    params["shifts"]["Normal"]["fixed_cost"] = st.number_input(

        "Normal Fixed Cost",

        value=params["shifts"]["Normal"]["fixed_cost"],

        step=1000

    )

    st.markdown("---")

    st.markdown("#### Extended Shift")

    params["shifts"]["Extended"]["capacity"] = st.number_input(

        "Extended Capacity",

        value=params["shifts"]["Extended"]["capacity"],

        step=100

    )

    params["shifts"]["Extended"]["fixed_cost"] = st.number_input(

        "Extended Fixed Cost",

        value=params["shifts"]["Extended"]["fixed_cost"],

        step=1000

    )

# ---------------------------------------------------------
# Cost Parameters
# ---------------------------------------------------------

with st.sidebar.expander("Cost Parameters"):

    params["holding_cost"] = st.number_input(

        "Holding Cost",

        value=params["holding_cost"]

    )

    params["switch_cost"] = st.number_input(

        "Switching Cost",

        value=params["switch_cost"],

        step=1000

    )

# ---------------------------------------------------------
# Inventory Parameters
# ---------------------------------------------------------

with st.sidebar.expander("Inventory"):

    params["initial_inventory"] = st.number_input(

        "Initial Inventory",

        value=params["initial_inventory"],

        step=100

    )

    params["ending_inventory"] = st.number_input(

        "Required Ending Inventory",

        value=params["ending_inventory"],

        step=100

    )

    params["min_production"] = st.number_input(

        "Minimum Production",

        value=params["min_production"],

        step=100

    )

st.sidebar.markdown("---")

# ---------------------------------------------------------
# Solve Button
# ---------------------------------------------------------

solve = st.sidebar.button(

    "🚀 Solve Optimization",

    use_container_width=True

)

# ---------------------------------------------------------
# Overview
# ---------------------------------------------------------

ui.show_overview(

    months,

    params["demand"]

)

# ---------------------------------------------------------
# Solve Model
# ---------------------------------------------------------

if solve:

    with st.spinner("Running MILP Optimization..."):

        st.session_state.results = solve_model(params)

results = st.session_state.results

# ---------------------------------------------------------
# Stop if nothing solved yet
# ---------------------------------------------------------

if results is None:

    st.info("Configure the model and click **Solve Optimization**.")

    st.stop()

if results["status"] != "Optimal":

    st.error(results["message"])

    st.stop()

summary = results["summary"]

costs = results["cost_breakdown"]

df = results["monthly_results"]

# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

ui.divider()

ui.show_metrics(summary, results)

ui.divider()

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

overview_tab, production_tab, inventory_tab, cost_tab, model_tab = st.tabs(
    [
        "📊 Overview",
        "🏭 Production",
        "📦 Inventory",
        "💰 Costs",
        "📘 Model"
    ]
)

# =========================================================
# OVERVIEW
# =========================================================

with overview_tab:

    col1, col2 = st.columns(2)

    with col1:

        st.plotly_chart(
            charts.production_vs_demand(
                results["production_df"]
            ),
            use_container_width=True
        )

    with col2:

        st.plotly_chart(
            charts.inventory_trend(
                results["inventory_df"]
            ),
            use_container_width=True,
            key="inventory_overview"
        )

    col3, col4 = st.columns(2)

    with col3:

        st.plotly_chart(
            charts.capacity_utilization(
                results["monthly_results"],
                params
            ),
            use_container_width=True
        )

    with col4:

        st.plotly_chart(
            charts.shift_timeline(
                results["shift_df"]
            ),
            use_container_width=True
        )

# =========================================================
# PRODUCTION
# =========================================================

with production_tab:

    st.subheader("Production Schedule")

    st.dataframe(
        results["monthly_results"],
        use_container_width=True,
        hide_index=True
    )

    st.plotly_chart(
        charts.production_heatmap(
            results["production_df"]
        ),
        use_container_width=True
    )

# =========================================================
# INVENTORY
# =========================================================

with inventory_tab:

    st.subheader("Inventory Levels")

    st.dataframe(
        results["inventory_df"],
        hide_index=True,
        use_container_width=True
    )

    st.plotly_chart(
        charts.inventory_trend(
            results["inventory_df"]
        ),
        use_container_width=True,
        key="inventory_tab"
    )

# =========================================================
# COSTS
# =========================================================

with cost_tab:

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            charts.cost_breakdown(
                costs
            ),
            use_container_width=True
        )

    with right:

        st.plotly_chart(
            charts.monthly_costs(
                results["monthly_results"],
                params
            ),
            use_container_width=True
        )

    st.subheader("Cost Summary")

    cost_df = pd.DataFrame({

        "Cost Component":[
            "Fixed Cost",
            "Holding Cost",
            "Switching Cost",
            "Total Cost"
        ],

        "Amount":[
            costs["Fixed Cost"],
            costs["Holding Cost"],
            costs["Switching Cost"],
            costs["Total Cost"]
        ]

    })

    st.dataframe(
        cost_df,
        hide_index=True,
        use_container_width=True
    )

# =========================================================
# MODEL
# =========================================================

with model_tab:

    st.subheader("MILP Formulation")

    st.latex(r"""
    \min Z =
    \sum_{t=1}^{T}\sum_{s}FC_sX_{t,s}
    +
    h\sum_{t=1}^{T}I_t
    +
    SC\sum_{t=2}^{T}Switch_t
    """)

    st.markdown("### Subject to")

    st.latex(r"I_0 + P_1 - D_1 = I_1")

    st.latex(r"I_{t-1}+P_t-D_t=I_t")

    st.latex(r"P_t\le\sum_s Capacity_sX_{t,s}")

    st.latex(r"P_t\ge MinProduction\sum_sX_{t,s}")

    st.latex(r"\sum_sX_{t,s}\le1")

    st.latex(r"I_T\ge EndingInventory")

    st.latex(r"I_t\ge0")

# ---------------------------------------------------------
# Constraint Checker
# ---------------------------------------------------------

ui.divider()

st.subheader("✅ Constraint Verification")

check_inventory = (
    results["monthly_results"]["Inventory"] >= 0
).all()

check_end = (
    results["monthly_results"].iloc[-1]["Inventory"]
    >=
    params["ending_inventory"]
)

check_capacity = (
    results["monthly_results"]["Production"]
    <=
    results["monthly_results"]["Capacity"]
).all()

check_min = True

for _, row in results["monthly_results"].iterrows():

    if row["Shift"] != "Idle":

        if row["Production"] < params["min_production"]:

            check_min = False

c1, c2 = st.columns(2)

with c1:

    ui.constraint_status(
        "Inventory Non-negative",
        check_inventory
    )

    ui.constraint_status(
        "Ending Inventory",
        check_end
    )

with c2:

    ui.constraint_status(
        "Capacity Constraints",
        check_capacity
    )

    ui.constraint_status(
        "Minimum Production",
        check_min
    )

# ---------------------------------------------------------
# Insights
# ---------------------------------------------------------

ui.divider()

st.subheader("💡 Business Insights")

for item in insights.generate_insights(
    results,
    params
):

    ui.insight(item)

# ---------------------------------------------------------
# Downloads
# ---------------------------------------------------------

ui.divider()

exports.download_buttons(
    st,
    results
)

# ---------------------------------------------------------
# Raw Results
# ---------------------------------------------------------

with st.expander("View Raw Optimization Results"):

    st.dataframe(
        results["monthly_results"],
        use_container_width=True
    )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

ui.footer()
