"""
Export utilities for Production Planning Dashboard
"""

import io
import pandas as pd


# -------------------------------------------------------
# CSV Export
# -------------------------------------------------------

def to_csv(df):

    """
    Returns CSV data as bytes.
    """

    return df.to_csv(index=False).encode("utf-8")


# -------------------------------------------------------
# Excel Export
# -------------------------------------------------------

def to_excel(results):

    """
    Creates an Excel workbook with multiple sheets.

    Sheets:
    1. Production Plan
    2. Cost Breakdown
    3. Summary
    """

    output = io.BytesIO()

    production_df = results["monthly_results"]

    cost_df = pd.DataFrame({

        "Cost Component":[

            "Fixed Cost",
            "Holding Cost",
            "Switching Cost",
            "Total Cost"

        ],

        "Amount":[

            results["cost_breakdown"]["Fixed Cost"],
            results["cost_breakdown"]["Holding Cost"],
            results["cost_breakdown"]["Switching Cost"],
            results["cost_breakdown"]["Total Cost"]

        ]

    })

    summary = results["summary"]

    summary_df = pd.DataFrame({

        "Metric":[

            "Total Cost",
            "Total Production",
            "Average Inventory",
            "Normal Shift Months",
            "Extended Shift Months",
            "Idle Months"

        ],

        "Value":[

            summary["Total Cost"],
            summary["Total Production"],
            summary["Average Inventory"],
            summary["Normal Months"],
            summary["Extended Months"],
            summary["Idle Months"]

        ]

    })

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        production_df.to_excel(

            writer,

            sheet_name="Production Plan",

            index=False

        )

        cost_df.to_excel(

            writer,

            sheet_name="Cost Breakdown",

            index=False

        )

        summary_df.to_excel(

            writer,

            sheet_name="Summary",

            index=False

        )

    output.seek(0)

    return output


# -------------------------------------------------------
# Download Buttons
# -------------------------------------------------------

def download_buttons(st, results):

    st.subheader("⬇ Download Results")

    csv_data = to_csv(
        results["monthly_results"]
    )

    excel_data = to_excel(results)

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(

            label="📄 Download CSV",

            data=csv_data,

            file_name="production_plan.csv",

            mime="text/csv",

            use_container_width=True

        )

    with col2:

        st.download_button(

            label="📊 Download Excel",

            data=excel_data,

            file_name="production_plan.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            use_container_width=True

        )
