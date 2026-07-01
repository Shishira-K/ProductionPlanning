"""
Business Insights Generator
"""


def generate_insights(results, params):

    summary = results["summary"]
    costs = results["cost_breakdown"]
    df = results["monthly_results"]

    insights = []

    # --------------------------------------------------
    # Peak Demand
    # --------------------------------------------------

    peak_demand = df.loc[df["Demand"].idxmax()]

    insights.append(
        f"Peak demand occurs in Month {int(peak_demand['Month'])} "
        f"with {peak_demand['Demand']:,.0f} units."
    )

    # --------------------------------------------------
    # Peak Production
    # --------------------------------------------------

    peak_prod = df.loc[df["Production"].idxmax()]

    insights.append(
        f"Maximum production is scheduled in Month "
        f"{int(peak_prod['Month'])} "
        f"({peak_prod['Production']:,.0f} units)."
    )

    # --------------------------------------------------
    # Ending Inventory
    # --------------------------------------------------

    ending_inventory = df.iloc[-1]["Inventory"]

    insights.append(
        f"Ending inventory is {ending_inventory:,.0f} units "
        f"against the required {params['ending_inventory']:,.0f} units."
    )

    # --------------------------------------------------
    # Extended Shift Usage
    # --------------------------------------------------

    ext = summary["Extended Months"]

    if ext == 0:

        insights.append(
            "The optimizer satisfies demand without using the Extended Shift."
        )

    else:

        insights.append(
            f"The Extended Shift is used during {ext} month(s) "
            "to satisfy higher production requirements."
        )

    # --------------------------------------------------
    # Idle Months
    # --------------------------------------------------

    idle = summary["Idle Months"]

    if idle > 0:

        insights.append(
            f"The plant remains idle during {idle} month(s)."
        )

    else:

        insights.append(
            "The plant operates every month."
        )

    # --------------------------------------------------
    # Holding Cost
    # --------------------------------------------------

    holding_pct = (
        costs["Holding Cost"]
        /
        costs["Total Cost"]
    ) * 100

    insights.append(
        f"Holding cost contributes "
        f"{holding_pct:.2f}% "
        f"of the total cost."
    )

    # --------------------------------------------------
    # Capacity Utilization
    # --------------------------------------------------

    utilization = []

    for _, row in df.iterrows():

        if row["Shift"] == "Normal":

            cap = params["shifts"]["Normal"]["capacity"]

        elif row["Shift"] == "Extended":

            cap = params["shifts"]["Extended"]["capacity"]

        else:

            continue

        utilization.append(
            row["Production"] / cap
        )

    if utilization:

        avg_util = sum(utilization) / len(utilization) * 100

        insights.append(
            f"Average capacity utilization is "
            f"{avg_util:.1f}%."
        )

    # --------------------------------------------------
    # Inventory Observation
    # --------------------------------------------------

    minimum_inventory = df["Inventory"].min()

    if minimum_inventory == 0:

        insights.append(
            "Inventory reaches zero during the planning horizon."
        )

    else:

        insights.append(
            f"The minimum inventory level maintained is "
            f"{minimum_inventory:,.0f} units."
        )

    # --------------------------------------------------
    # Switching Count
    # --------------------------------------------------

    switches = 0

    previous = None

    for shift in df["Shift"]:

        if previous == "Normal" and shift == "Extended":

            switches += 1

        previous = shift

    insights.append(
        f"The production schedule contains "
        f"{switches} Normal → Extended shift transition(s)."
    )

    # --------------------------------------------------
    # Total Cost
    # --------------------------------------------------

    insights.append(
        f"The optimized production plan results in a total cost of "
        f"£{summary['Total Cost']:,.0f}."
    )

    return insights
