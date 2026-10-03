"""
modules/dispatch.py
----------------------------------------------------------------------
Module 1 — Dispatch, Tonnage & Labor Group Payment.

Handles:
    * Three dispatch methods (Robot / Manual / Bulk) with conditional
      field logic driven by an @st.fragment, so toggling the method
      only reruns this small section instead of the whole app.
    * Truck Plate No. AND Trailer/Power Unit Plate No. are ALWAYS
      visible and writable, regardless of dispatch method — matching
      the factory's real Daily Dispatch Record Sheet, which records
      both truck-related plates on every entry (Robot, Manual, or
      Bulk alike). Both are optional; left blank they're stored as
      two blank spaces ("  ").
    * The automated payment-calculation engine.
    * Persistence to dispatch_data.csv.
    * Filterable breakdown table + CSV/Excel export.
----------------------------------------------------------------------
"""

from datetime import date

import pandas as pd
import streamlit as st

from translations import tr
from utils import DISPATCH_CSV, append_row, download_buttons, load_csv, safe_sorted_unique

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
RATE_PER_TON_BIRR = 20.0  # Manual Packaging Line labor pay ONLY

ROBOT_LINES = [f"Line {i}" for i in range(1, 11)]
MANUAL_LINES = [f"Manual Line {i}" for i in range(1, 6)]
LABOR_GROUPS = [f"Group {i}" for i in range(1, 5)]

METHOD_ROBOT = "robot"
METHOD_MANUAL = "manual"
METHOD_BULK = "bulk"

BLANK_PLATE = "  "  # two blank spaces, per spec, when the field is hidden

COLUMNS = [
    "Date",
    "Shift",
    "CementType",
    "DispatchMethod",
    "PackagingLine",
    "LaborGroup",
    "TruckPlateNumber",
    "TrailerPlateNumber",
    "InitialLoadedTonnage",
    "ReturnedOverloadTonnage",
    "NetTonnage",
    "PenaltyType",
    "PenaltyBirr",
    "PenaltyTonnage",
    "GrossPayBirr",
    "TotalPenaltyBirr",
    "NetPayableBirr",
]


# ----------------------------------------------------------------------
# Calculation engine
# ----------------------------------------------------------------------
def calculate_payment(
    method: str,
    initial_tonnage: float,
    returned_tonnage: float,
    penalty_birr: float,
    penalty_tonnage: float,
) -> dict:
    """Apply the fixed formula rules and return every derived figure.

    Gross Pay (20 Birr/ton labor payment) only applies to the Manual
    Packaging Line — Robot lines and Bulk Loading involve no manual
    labor group, so their Gross Pay is fixed at 0.
    """
    net_tonnage = initial_tonnage - returned_tonnage

    if method == METHOD_MANUAL:
        gross_pay = net_tonnage * RATE_PER_TON_BIRR
        total_penalty = penalty_birr + (penalty_tonnage * RATE_PER_TON_BIRR)
    else:
        gross_pay = 0.0
        total_penalty = 0.0

    net_payable = gross_pay - total_penalty

    return {
        "NetTonnage": round(net_tonnage, 2),
        "GrossPayBirr": round(gross_pay, 2),
        "TotalPenaltyBirr": round(total_penalty, 2),
        "NetPayableBirr": round(net_payable, 2),
    }


# ----------------------------------------------------------------------
# UI — the conditional entry form lives inside a fragment so that
# switching Dispatch Method re-renders only this block (fast) instead
# of triggering a full-page rerun.
# ----------------------------------------------------------------------
@st.fragment
def _dispatch_entry_fragment(lang: str) -> None:
    method_display = {
        tr("method_robot", lang): METHOD_ROBOT,
        tr("method_manual", lang): METHOD_MANUAL,
        tr("method_bulk", lang): METHOD_BULK,
    }

    st.markdown(f"**{tr('dispatch_method_label', lang)}**")
    method_label = st.radio(
        tr("dispatch_method_label", lang),
        list(method_display.keys()),
        horizontal=True,
        label_visibility="collapsed",
        key="dispatch_method_choice",
    )
    method = method_display[method_label]

    # These two dropdowns are also outside the form since they depend on
    # `method` and must react immediately when the radio button changes.
    packaging_line, labor_group = "N/A", "N/A"
    c_line, c_group = st.columns(2)
    if method == METHOD_ROBOT:
        with c_line:
            packaging_line = st.selectbox(tr("packaging_line_label", lang), ROBOT_LINES, key="robot_line")
    elif method == METHOD_MANUAL:
        with c_line:
            packaging_line = st.selectbox(tr("packaging_line_label", lang), MANUAL_LINES, key="manual_line")
        with c_group:
            labor_group = st.selectbox(tr("labor_group_label", lang), LABOR_GROUPS, key="manual_group")

    # ------------------------------------------------------------------
    # The rest of the data-entry fields are batched inside st.form so
    # typing/adjusting numbers doesn't trigger a rerun until submission.
    # ------------------------------------------------------------------
    with st.form("dispatch_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            entry_date = st.date_input(tr("date_label", lang), value=date.today())
        with c2:
            cement_type = st.selectbox(tr("cement_type_label", lang), ["OPC", "PPC"])
        with c3:
            if method in (METHOD_ROBOT, METHOD_MANUAL):
                shift = st.selectbox(
                    tr("shift_label", lang), [tr("shift_a", lang), tr("shift_b", lang)]
                )
            else:
                shift = "N/A"
                st.text_input(tr("shift_label", lang), value="N/A", disabled=True)

        # Real dispatch records — Robot, Manual, or Bulk alike — always
        # capture both the truck's own plate and its trailer/power-unit
        # plate (matching the factory's actual Daily Dispatch Record
        # Sheet). Neither field is restricted by dispatch method.
        c4, c5 = st.columns(2)
        with c4:
            truck_plate = st.text_input(tr("truck_plate_label", lang))
        with c5:
            trailer_plate = st.text_input(tr("trailer_plate_label", lang))

        st.markdown("---")
        c6, c7 = st.columns(2)
        with c6:
            initial_tonnage = st.number_input(
                tr("initial_tonnage_label", lang), min_value=0.0, step=0.1, format="%.2f"
            )
        with c7:
            returned_tonnage = st.number_input(
                tr("returned_tonnage_label", lang), min_value=0.0, step=0.1, format="%.2f"
            )

        penalty_birr, penalty_tonnage = 0.0, 0.0
        penalty_type = tr("penalty_none", lang)
        if method == METHOD_MANUAL:
            st.markdown(f"**{tr('penalty_type_label', lang)}**")
            c8, c9 = st.columns(2)
            with c8:
                penalty_options = [
                    tr("penalty_none", lang),
                    tr("penalty_birr_opt", lang),
                    tr("penalty_tonnage_opt", lang),
                ]
                penalty_type = st.selectbox(
                    tr("penalty_type_label", lang), penalty_options, label_visibility="collapsed"
                )
            with c9:
                if penalty_type == tr("penalty_birr_opt", lang):
                    penalty_birr = st.number_input(
                        tr("penalty_amount_birr_label", lang), min_value=0.0, step=1.0, format="%.2f"
                    )
                elif penalty_type == tr("penalty_tonnage_opt", lang):
                    penalty_tonnage = st.number_input(
                        tr("penalty_amount_ton_label", lang), min_value=0.0, step=0.1, format="%.2f"
                    )

        submitted = st.form_submit_button(tr("save_record_button", lang), use_container_width=True)

    if submitted:
        # Both plate fields are optional on every dispatch method — if left
        # blank they're stored as two blank spaces, never blocking the save.
        final_plate = truck_plate.strip().upper() if truck_plate and truck_plate.strip() else BLANK_PLATE
        final_trailer = trailer_plate.strip().upper() if trailer_plate and trailer_plate.strip() else BLANK_PLATE

        results = calculate_payment(method, initial_tonnage, returned_tonnage, penalty_birr, penalty_tonnage)

        row = {
            "Date": entry_date.strftime("%Y-%m-%d"),
            "Shift": shift,
            "CementType": cement_type,
            "DispatchMethod": method_label,
            "PackagingLine": packaging_line,
            "LaborGroup": labor_group,
            "TruckPlateNumber": final_plate,
            "TrailerPlateNumber": final_trailer,
            "InitialLoadedTonnage": round(initial_tonnage, 2),
            "ReturnedOverloadTonnage": round(returned_tonnage, 2),
            "PenaltyType": penalty_type,
            "PenaltyBirr": round(penalty_birr, 2),
            "PenaltyTonnage": round(penalty_tonnage, 2),
            **results,
        }

        append_row(DISPATCH_CSV, COLUMNS, row)
        st.success(tr("record_saved_success", lang))

        st.markdown(f"#### {tr('calc_result_header', lang)}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(tr("net_tonnage_metric", lang), f"{results['NetTonnage']} t")
        m2.metric(tr("gross_pay_metric", lang), f"{results['GrossPayBirr']:,.2f} Birr")
        m3.metric(tr("total_penalty_metric", lang), f"{results['TotalPenaltyBirr']:,.2f} Birr")
        m4.metric(tr("net_payable_metric", lang), f"{results['NetPayableBirr']:,.2f} Birr")


def render(lang: str) -> None:
    st.header(tr("m1_header", lang))
    st.caption(tr("sidebar_company", lang))

    _dispatch_entry_fragment(lang)

    # ------------------------------------------------------------------
    # Breakdown table & export
    # ------------------------------------------------------------------
    st.divider()
    st.subheader(tr("breakdown_header", lang))

    all_data = load_csv(DISPATCH_CSV, COLUMNS)

    if all_data.empty:
        st.info(tr("no_dispatch_data_msg", lang))
        return

    f1, f2, f3 = st.columns(3)
    with f1:
        dates_available = safe_sorted_unique(all_data["Date"], reverse=True)
        date_filter = st.multiselect(tr("filter_date_label", lang), dates_available)
    with f2:
        shift_filter = st.multiselect(
            tr("filter_shift_label", lang), safe_sorted_unique(all_data["Shift"])
        )
    with f3:
        method_filter = st.multiselect(
            tr("filter_method_label", lang), safe_sorted_unique(all_data["DispatchMethod"])
        )

    filtered = all_data.copy()
    if date_filter:
        filtered = filtered[filtered["Date"].isin(date_filter)]
    if shift_filter:
        filtered = filtered[filtered["Shift"].isin(shift_filter)]
    if method_filter:
        filtered = filtered[filtered["DispatchMethod"].isin(method_filter)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    s1, s2, s3 = st.columns(3)
    s1.metric(tr("total_records_metric", lang), len(filtered))
    s2.metric(tr("total_net_tonnage_metric", lang), f"{filtered['NetTonnage'].sum():,.2f} t")
    s3.metric(tr("total_net_payable_metric", lang), f"{filtered['NetPayableBirr'].sum():,.2f} Birr")

    st.markdown(f"#### {tr('export_header', lang)}")
    download_buttons(filtered, "dispatch_report", "dispatch")
