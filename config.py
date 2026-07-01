"""
Configuration file for Production Planning Dashboard
"""

BASE_CASE = {
    "months": 6,

    "demand": [
        6000,
        6500,
        7500,
        7000,
        6000,
        6000
    ],

    "shifts": {

        "Normal": {

            "capacity": 5000,
            "fixed_cost": 100000

        },

        "Extended": {

            "capacity": 7500,
            "fixed_cost": 180000

        }

    },

    "holding_cost": 2,

    "switch_cost": 15000,

    "min_production": 2000,

    "initial_inventory": 3000,

    "ending_inventory": 2000

}
