import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# -------------------------------------------------------
# Production vs Demand
# -------------------------------------------------------

def production_vs_demand(df):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["Month"],
            y=df["Production"],
            name="Production"
        )
    )

    fig.add_trace(
        go.Bar(
            x=df["Month"],
            y=df["Demand"],
            name="Demand"
        )
    )

    fig.update_layout(
        title="Production vs Demand",
        xaxis_title="Month",
        yaxis_title="Units",
        barmode="group",
        height=450,
        template="plotly_white"
    )

    return fig


# -------------------------------------------------------
# Inventory Trend
# -------------------------------------------------------

def inventory_trend(df):

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df["Month"],
            y=df["Inventory"],
            mode="lines+markers",
            fill="tozeroy",
            name="Inventory"

        )

    )

    fig.update_layout(

        title="Inventory Trend",
        xaxis_title="Month",
        yaxis_title="Inventory",
        height=450,
        template="plotly_white"

    )

    return fig


# -------------------------------------------------------
# Capacity Utilization
# -------------------------------------------------------

def capacity_utilization(df, params):

    util = []

    for _, row in df.iterrows():

        if row["Shift"] == "Normal":

            cap = params["shifts"]["Normal"]["capacity"]

        elif row["Shift"] == "Extended":

            cap = params["shifts"]["Extended"]["capacity"]

        else:

            cap = 1

        util.append(

            row["Production"] / cap * 100

            if cap > 0 else 0

        )

    fig = px.bar(

        x=df["Month"],
        y=util,
        text=[f"{x:.1f}%" for x in util]

    )

    fig.update_layout(

        title="Capacity Utilization",
        xaxis_title="Month",
        yaxis_title="Utilization (%)",
        height=450,
        template="plotly_white"

    )

    return fig


# -------------------------------------------------------
# Cost Breakdown
# -------------------------------------------------------

def cost_breakdown(costs):

    cost_df = pd.DataFrame({

        "Component":[

            "Fixed Cost",
            "Holding Cost",
            "Switching Cost"

        ],

        "Cost":[

            costs["Fixed Cost"],
            costs["Holding Cost"],
            costs["Switching Cost"]

        ]

    })

    fig = px.pie(

        cost_df,

        names="Component",

        values="Cost",

        hole=.45

    )

    fig.update_layout(

        title="Cost Breakdown",
        height=450,
        template="plotly_white"

    )

    return fig


# -------------------------------------------------------
# Monthly Cost Distribution
# -------------------------------------------------------

def monthly_costs(df, params):

    fixed = []

    holding = []

    switching = []

    previous_shift = None

    for _, row in df.iterrows():

        if row["Shift"] == "Normal":

            fixed.append(
                params["shifts"]["Normal"]["fixed_cost"]
            )

        elif row["Shift"] == "Extended":

            fixed.append(
                params["shifts"]["Extended"]["fixed_cost"]
            )

        else:

            fixed.append(0)

        holding.append(

            row["Inventory"]

            *

            params["holding_cost"]

        )

        if previous_shift == "Normal" and row["Shift"] == "Extended":

            switching.append(

                params["switch_cost"]

            )

        else:

            switching.append(0)

        previous_shift = row["Shift"]

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=df["Month"],
            y=fixed,
            name="Fixed"

        )

    )

    fig.add_trace(

        go.Bar(

            x=df["Month"],
            y=holding,
            name="Holding"

        )

    )

    fig.add_trace(

        go.Bar(

            x=df["Month"],
            y=switching,
            name="Switching"

        )

    )

    fig.update_layout(

        title="Monthly Cost Distribution",
        barmode="stack",
        height=450,
        template="plotly_white"

    )

    return fig


# -------------------------------------------------------
# Shift Timeline
# -------------------------------------------------------

def shift_timeline(df):

    colors = {

        "Normal": "#2563EB",

        "Extended": "#16A34A",

        "Idle": "#D1D5DB"

    }

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=df["Month"],

            y=[1] * len(df),

            marker_color=[

                colors[s]

                for s in df["Shift"]

            ],

            text=df["Shift"],

            textposition="inside",

            showlegend=False

        )

    )

    fig.update_yaxes(

        visible=False

    )

    fig.update_layout(

        title="Shift Schedule",
        height=250,
        template="plotly_white"

    )

    return fig


# -------------------------------------------------------
# Production Heatmap
# -------------------------------------------------------

def production_heatmap(df):

    fig = px.imshow(

        [df["Production"].tolist()],

        labels=dict(

            x="Month",

            color="Production"

        ),

        x=df["Month"],

        y=["Production"],

        aspect="auto"

    )

    fig.update_layout(

        title="Production Heatmap",
        height=250,
        template="plotly_white"

    )

    return fig
