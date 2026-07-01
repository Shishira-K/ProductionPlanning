import time
import pandas as pd
import pulp as pl


def solve_model(params):
    """
    Solves the Production Planning MILP.

    Parameters
    ----------
    params : dict

        {
            "months": 6,
            "demand": [...],
            "shifts": {
                "Normal": {
                    "capacity":5000,
                    "fixed_cost":100000
                },
                "Extended":{
                    "capacity":7500,
                    "fixed_cost":180000
                }
            },
            "holding_cost":2,
            "switch_cost":15000,
            "min_production":2000,
            "initial_inventory":3000,
            "ending_inventory":2000
        }

    Returns
    -------
    Dictionary containing optimization results.
    """

    start = time.time()

    # -------------------------------
    # Read Parameters
    # -------------------------------

    n_months = params["months"]
    demand = params["demand"]

    shifts = params["shifts"]

    holding_cost = params["holding_cost"]
    switch_cost = params["switch_cost"]

    min_prod = params["min_production"]

    initial_inventory = params["initial_inventory"]
    ending_inventory = params["ending_inventory"]

    months = list(range(n_months))
    shift_names = list(shifts.keys())

    # -------------------------------
    # Model
    # -------------------------------

    model = pl.LpProblem(
        "Production_Planning",
        pl.LpMinimize
    )

    # -------------------------------
    # Decision Variables
    # -------------------------------

    production = pl.LpVariable.dicts(
        "Production",
        months,
        lowBound=0
    )

    inventory = pl.LpVariable.dicts(
        "Inventory",
        months,
        lowBound=0
    )

    shift = pl.LpVariable.dicts(
        "Shift",
        [(m, s) for m in months for s in shift_names],
        cat="Binary"
    )

    switch = pl.LpVariable.dicts(
        "Switch",
        months[1:],
        cat="Binary"
    )

    # -------------------------------
    # Objective Function
    # -------------------------------

    fixed_shift_cost = pl.lpSum(

        shifts[s]["fixed_cost"] * shift[(m, s)]

        for m in months
        for s in shift_names

    )

    inventory_cost = holding_cost * pl.lpSum(
        inventory[m]
        for m in months
    )

    switching_cost = switch_cost * pl.lpSum(
        switch[m]
        for m in months[1:]
    )

    model += (
        fixed_shift_cost
        + inventory_cost
        + switching_cost
    )

    # -------------------------------
    # Inventory Balance
    # -------------------------------

    model += (
        initial_inventory
        + production[0]
        - demand[0]
        == inventory[0]
    )

    for m in months[1:]:

        model += (
            inventory[m - 1]
            + production[m]
            - demand[m]
            == inventory[m]
        )

    # -------------------------------
    # Capacity Constraints
    # -------------------------------

    for m in months:

        capacity_expr = pl.lpSum(

            shifts[s]["capacity"] * shift[(m, s)]

            for s in shift_names

        )

        model += (
            production[m]
            <= capacity_expr
        )

    # -------------------------------
    # Minimum Production
    # -------------------------------

    for m in months:

        model += (

            production[m]

            >=

            min_prod *

            pl.lpSum(
                shift[(m, s)]
                for s in shift_names
            )

        )

    # -------------------------------
    # Only One Shift
    # -------------------------------

    for m in months:

        model += (

            pl.lpSum(

                shift[(m, s)]

                for s in shift_names

            )

            <= 1

        )

    # -------------------------------
    # Ending Inventory
    # -------------------------------

    model += (

        inventory[n_months - 1]

        >=

        ending_inventory

    )

    # -------------------------------
    # Switching Constraint
    #
    # Only applies:
    #
    # Normal -> Extended
    # -------------------------------

    if "Normal" in shift_names and "Extended" in shift_names:

        for m in months[1:]:

            model += (

                switch[m]

                >=

                shift[(m - 1, "Normal")]

                +

                shift[(m, "Extended")]

                -

                1

            )

    # -------------------------------
    # Solve
    # -------------------------------

    solver = pl.PULP_CBC_CMD(msg=False)

    model.solve(solver)

    elapsed = time.time() - start

    status = pl.LpStatus[model.status]

    # ----------------------------------------
    # Infeasible
    # ----------------------------------------

    if status != "Optimal":

        return {

            "status": status,

            "message": "No feasible solution found."

        }

    # ----------------------------------------
    # Extract Results
    # ----------------------------------------

    rows = []

    total_prod = 0
    total_inventory = 0

    normal_months = 0
    extended_months = 0
    idle_months = 0

    monthly_fixed_cost = []
    monthly_holding_cost = []
    monthly_switching_cost = []
    capacity_used = []

    previous_shift = None

    for m in months:

        prod = production[m].value()
        inv = inventory[m].value()

        shift_used = "Idle"

        for s in shift_names:
            if shift[(m, s)].value() > 0.5:
                shift_used = s

        if shift_used == "Normal":
            normal_months += 1
            capacity = shifts["Normal"]["capacity"]
            fixed = shifts["Normal"]["fixed_cost"]

        elif shift_used == "Extended":
            extended_months += 1
            capacity = shifts["Extended"]["capacity"]
            fixed = shifts["Extended"]["fixed_cost"]

        else:
            idle_months += 1
            capacity = 0
            fixed = 0

        if previous_shift == "Normal" and shift_used == "Extended":
            switch_cost_month = switch_cost
        else:
            switch_cost_month = 0

        previous_shift = shift_used

        holding = inv * holding_cost

        utilization = (
            prod / capacity * 100
            if capacity > 0 else 0
        )

        total_prod += prod
        total_inventory += inv

        monthly_fixed_cost.append(fixed)
        monthly_holding_cost.append(holding)
        monthly_switching_cost.append(switch_cost_month)
        capacity_used.append(utilization)

        rows.append({

            "Month": m + 1,

            "Demand": demand[m],

            "Production": prod,

            "Inventory": inv,

            "Shift": shift_used,

            "Capacity": capacity,

            "Capacity Utilization (%)": round(utilization,2),

            "Fixed Cost": fixed,

            "Holding Cost": holding,

            "Switching Cost": switch_cost_month

        })

    results_df = pd.DataFrame(rows)

    

    # ----------------------------------------
    # Cost Breakdown
    # ----------------------------------------

    fixed_cost = sum(monthly_fixed_cost)

    holding = sum(monthly_holding_cost)

    switching = sum(monthly_switching_cost)

    total_cost = pl.value(model.objective)

    costs = {

        "Fixed Cost": fixed_cost,

        "Holding Cost": holding,

        "Switching Cost": switching,

        "Total Cost": total_cost

    }

    summary = {

        "Total Cost": total_cost,

        "Total Production": total_prod,

        "Average Inventory": total_inventory / n_months,

        "Normal Months": normal_months,

        "Extended Months": extended_months,

        "Idle Months": idle_months

    }

    costs = {

        "Fixed Cost": fixed_cost,

        "Holding Cost": holding,

        "Switching Cost": switching,

        "Total Cost": total_cost

    }


    production_df = results_df[
        ["Month", "Demand", "Production"]
    ]

    inventory_df = results_df[
        ["Month", "Inventory"]
    ]

    capacity_df = results_df[
        ["Month", "Capacity Utilization (%)"]
    ]

    shift_df = results_df[
        ["Month", "Shift"]
    ]

    monthly_cost_df = results_df[
        [
            "Month",
            "Fixed Cost",
            "Holding Cost",
            "Switching Cost"
        ]
    ]

    return {

        "status": status,

        "objective": total_cost,

        "summary": summary,

        "cost_breakdown": costs,

        "monthly_results": results_df,

        "production_df": production_df,

        "inventory_df": inventory_df,

        "capacity_df": capacity_df,

        "shift_df": shift_df,

        "monthly_cost_df": monthly_cost_df,

        "solver_time": round(elapsed,4),

        "num_variables": len(model.variables()),

        "num_constraints": len(model.constraints())

    }
