"""
modules/attendance.py
----------------------------------------------------------------------
Module 2 — HR Attendance & Overtime Tracker.

This plant runs 24/7 on two shifts, so attendance is tracked per shift
— not per half-day — using the exact same shift naming as Module 1:

    Shift A (Day)    Shift B (Night)

...with the same status codes used on the factory floor:

    ✓  Present
    R  Rest Day
    SL Sick Leave
    AL Annual Leave
    X  Absent

Everything still lives in ONE single editable table — Employee Name,
Position, Shift A status, Shift B status, Overtime Hours, Overtime
Rate, and Overtime Pay (auto-calculated) — with no separate
roster/preview tables.

Overtime remains a direct Birr calculation:
    Overtime Pay (Birr) = Overtime Hours × Overtime Rate (Birr/hour)

Since Sunday/Holiday pay differs from a regular working day at this
plant, every entry carries an explicit, visible "Day Type" field
(Regular Working Day / Sunday / Public Holiday) — auto-suggested from
the selected date but always editable, and saved + exported as its
own column so payroll can see and filter by it directly, instead of
it being a hidden flag.

All unique-value lists that feed filter dropdowns go through
`safe_sorted_unique()` so a stray blank/NaN cell in older data can
never crash the page again.
----------------------------------------------------------------------
"""

from datetime import date

import pandas as pd
import streamlit as st

from translations import tr
from utils import ATTENDANCE_CSV, EMPLOYEES_CSV, append_rows, download_buttons, load_csv, safe_sorted_unique

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
EMPLOYEE_COLUMNS = ["FullName", "Position"]

ATTENDANCE_COLUMNS = [
    "Date",
    "DayType",
    "EmployeeName",
    "Position",
    "DayShiftStatus",
    "NightShiftStatus",
    "OvertimeHours",
    "OvertimeRateBirr",
    "OvertimePayBirr",
]

WORK_TABLE_KEY = "attendance_work_table"
EDITOR_WIDGET_KEY = "attendance_single_editor"


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _status_options(lang: str) -> list:
    return [
        tr("status_present", lang),
        tr("status_rest", lang),
        tr("status_sick_leave", lang),
        tr("status_annual_leave", lang),
        tr("status_absent", lang),
    ]


def _init_work_table(lang: str) -> pd.DataFrame:
    """Build the starting table: known employees from employees.csv, or one blank row."""
    known = load_csv(EMPLOYEES_CSV, EMPLOYEE_COLUMNS)
    present_label = tr("status_present", lang)

    if known.empty:
        return pd.DataFrame(
            [{
                "EmployeeName": "",
                "Position": "",
                "DayShiftStatus": present_label,
                "NightShiftStatus": present_label,
                "OvertimeHours": 0.0,
                "OvertimeRateBirr": 0.0,
                "OvertimePayBirr": 0.0,
            }]
        )

    return pd.DataFrame(
        {
            "EmployeeName": known["FullName"],
            "Position": known["Position"],
            "DayShiftStatus": present_label,
            "NightShiftStatus": present_label,
            "OvertimeHours": 0.0,
            "OvertimeRateBirr": 0.0,
            "OvertimePayBirr": 0.0,
        }
    )


def _recalculate_pay(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["OvertimeHours"] = pd.to_numeric(df["OvertimeHours"], errors="coerce").fillna(0.0)
    df["OvertimeRateBirr"] = pd.to_numeric(df["OvertimeRateBirr"], errors="coerce").fillna(0.0)
    df["OvertimePayBirr"] = (df["OvertimeHours"] * df["OvertimeRateBirr"]).round(2)
    return df


def _persist_known_employees(df: pd.DataFrame) -> None:
    """Silently remember distinct Name/Position pairs so the table pre-fills next time."""
    names = df[df["EmployeeName"].astype(str).str.strip() != ""]
    if names.empty:
        return
    unique = names[["EmployeeName", "Position"]].drop_duplicates(subset="EmployeeName", keep="last")
    unique = unique.rename(columns={"EmployeeName": "FullName"})
    unique.to_csv(EMPLOYEES_CSV, index=False)


# ----------------------------------------------------------------------
# Main render
# ----------------------------------------------------------------------
def render(lang: str) -> None:
    st.header(tr("m2_header", lang))
    st.caption(tr("sidebar_company", lang))

    st.subheader(tr("attendance_entry_header", lang))

    shift_a_label = tr("shift_a", lang)
    shift_b_label = tr("shift_b", lang)

    day_type_options = [tr("day_type_regular", lang), tr("day_type_sunday", lang), tr("day_type_holiday", lang)]

    c1, c2 = st.columns(2)
    with c1:
        entry_date = st.date_input(tr("date_label", lang), value=date.today(), key="attendance_date")

    # Auto-suggest the Day Type from the selected date's weekday (Sunday →
    # "Sunday", otherwise "Regular"), but only when the date actually
    # changes — so a manual override isn't silently reset by unrelated
    # reruns (e.g. editing a table cell).
    suggested_day_type = day_type_options[1] if entry_date.weekday() == 6 else day_type_options[0]
    if st.session_state.get("attendance_last_date") != entry_date:
        st.session_state["attendance_day_type"] = suggested_day_type
        st.session_state["attendance_last_date"] = entry_date

    with c2:
        day_type = st.selectbox(tr("day_type_label", lang), day_type_options, key="attendance_day_type")
    st.caption(f"ℹ️ {tr('day_type_auto_note', lang)}")

    status_options = _status_options(lang)

    # ------------------------------------------------------------------
    # Initialize / recompute the single working table BEFORE rendering
    # the editor, so any prior edits are reflected in OvertimePayBirr.
    # ------------------------------------------------------------------
    if WORK_TABLE_KEY not in st.session_state:
        st.session_state[WORK_TABLE_KEY] = _init_work_table(lang)

    st.session_state[WORK_TABLE_KEY] = _recalculate_pay(st.session_state[WORK_TABLE_KEY])

    st.caption(f"ℹ️ {tr('single_table_caption', lang)}")

    edited = st.data_editor(
        st.session_state[WORK_TABLE_KEY],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "EmployeeName": st.column_config.TextColumn(tr("employee_name_label", lang), required=True),
            "Position": st.column_config.TextColumn(tr("position_label", lang)),
            "DayShiftStatus": st.column_config.SelectboxColumn(
                shift_a_label, options=status_options, required=True
            ),
            "NightShiftStatus": st.column_config.SelectboxColumn(
                shift_b_label, options=status_options, required=True
            ),
            "OvertimeHours": st.column_config.NumberColumn(
                tr("ot_hours_col", lang), min_value=0.0, max_value=12.0, step=0.5, format="%.1f"
            ),
            "OvertimeRateBirr": st.column_config.NumberColumn(
                tr("overtime_rate_label", lang), min_value=0.0, step=5.0, format="%.2f"
            ),
            "OvertimePayBirr": st.column_config.NumberColumn(
                tr("overtime_pay_label", lang), format="%.2f", disabled=True
            ),
        },
        key=EDITOR_WIDGET_KEY,
    )

    # Recompute pay on the just-edited data and store it back so the
    # NEXT rerun (triggered automatically by any cell edit) displays
    # the freshly calculated Overtime Pay inside this same table.
    edited = _recalculate_pay(edited)
    st.session_state[WORK_TABLE_KEY] = edited

    if st.button(tr("save_attendance_button", lang), use_container_width=True):
        to_save = edited[edited["EmployeeName"].astype(str).str.strip() != ""].copy()

        if to_save.empty:
            st.warning(tr("no_employee_selected_warning", lang))
        else:
            present_label = tr("status_present", lang)
            to_save["DayShiftStatus"] = to_save["DayShiftStatus"].fillna(present_label)
            to_save["NightShiftStatus"] = to_save["NightShiftStatus"].fillna(present_label)

            # Overtime only counts if the employee was present on at least
            # one of the two shifts that day (matches real practice: no OT
            # on a rest/leave/absent day).
            worked_at_all = (to_save["DayShiftStatus"] == present_label) | (to_save["NightShiftStatus"] == present_label)
            to_save.loc[~worked_at_all, ["OvertimeHours", "OvertimePayBirr"]] = 0.0

            records = [
                {
                    "Date": entry_date.strftime("%Y-%m-%d"),
                    "DayType": day_type,
                    "EmployeeName": r.EmployeeName,
                    "Position": r.Position,
                    "DayShiftStatus": r.DayShiftStatus,
                    "NightShiftStatus": r.NightShiftStatus,
                    "OvertimeHours": round(float(r.OvertimeHours), 1),
                    "OvertimeRateBirr": round(float(r.OvertimeRateBirr), 2),
                    "OvertimePayBirr": round(float(r.OvertimePayBirr), 2),
                }
                for r in to_save.itertuples(index=False)
            ]
            append_rows(ATTENDANCE_CSV, ATTENDANCE_COLUMNS, records)
            _persist_known_employees(to_save)

            # Reset hours/rate/pay for the next entry, but keep names & positions.
            reset_df = to_save[["EmployeeName", "Position"]].copy()
            reset_df["DayShiftStatus"] = present_label
            reset_df["NightShiftStatus"] = present_label
            reset_df["OvertimeHours"] = 0.0
            reset_df["OvertimeRateBirr"] = 0.0
            reset_df["OvertimePayBirr"] = 0.0
            st.session_state[WORK_TABLE_KEY] = reset_df
            if EDITOR_WIDGET_KEY in st.session_state:
                del st.session_state[EDITOR_WIDGET_KEY]  # force the editor to reload the reset data

            st.success(f"{tr('attendance_saved_success', lang)} ({len(records)})")
            st.rerun()

    # ------------------------------------------------------------------
    # HR summary — filterable by Date AND Employee Name
    # ------------------------------------------------------------------
    st.divider()
    st.subheader(tr("summary_header", lang))

    history = load_csv(ATTENDANCE_CSV, ATTENDANCE_COLUMNS)

    if history.empty:
        st.info(tr("no_attendance_data_msg", lang))
        return

    history["OvertimeHours"] = pd.to_numeric(history["OvertimeHours"], errors="coerce").fillna(0.0)
    history["OvertimePayBirr"] = pd.to_numeric(history["OvertimePayBirr"], errors="coerce").fillna(0.0)

    f1, f2, f3 = st.columns(3)
    with f1:
        date_range = safe_sorted_unique(history["Date"], reverse=True)
        date_filter = st.multiselect(tr("filter_summary_date_label", lang), date_range)
    with f2:
        name_range = safe_sorted_unique(history["EmployeeName"])
        name_filter = st.multiselect(tr("filter_summary_name_label", lang), name_range)
    with f3:
        daytype_range = safe_sorted_unique(history["DayType"])
        daytype_filter = st.multiselect(tr("filter_summary_daytype_label", lang), daytype_range)

    scoped = history.copy()
    if date_filter:
        scoped = scoped[scoped["Date"].isin(date_filter)]
    if name_filter:
        scoped = scoped[scoped["EmployeeName"].isin(name_filter)]
    if daytype_filter:
        scoped = scoped[scoped["DayType"].isin(daytype_filter)]

    present_label = tr("status_present", lang)
    sick_label = tr("status_sick_leave", lang)
    annual_label = tr("status_annual_leave", lang)
    absent_label = tr("status_absent", lang)

    def _count_status(status_col: str, label: str, out_name: str) -> pd.Series:
        return scoped[scoped[status_col] == label].groupby("EmployeeName").size().rename(out_name)

    # Shift-attendance units present (Day + Night), summarized as full-day-equivalents.
    present_shifts = (
        (scoped["DayShiftStatus"] == present_label).astype(int)
        + (scoped["NightShiftStatus"] == present_label).astype(int)
    )
    scoped = scoped.assign(_PresentShiftUnits=present_shifts)
    present_days_equiv = (scoped.groupby("EmployeeName")["_PresentShiftUnits"].sum() / 2).rename("TotalPresentDays")

    sick_count = (
        _count_status("DayShiftStatus", sick_label, "SL_Day").add(
            _count_status("NightShiftStatus", sick_label, "SL_Night"), fill_value=0
        )
    ).rename("TotalSickLeaveShifts")
    annual_count = (
        _count_status("DayShiftStatus", annual_label, "AL_Day").add(
            _count_status("NightShiftStatus", annual_label, "AL_Night"), fill_value=0
        )
    ).rename("TotalAnnualLeaveShifts")
    absent_count = (
        _count_status("DayShiftStatus", absent_label, "X_Day").add(
            _count_status("NightShiftStatus", absent_label, "X_Night"), fill_value=0
        )
    ).rename("TotalAbsentShifts")
    ot_pay_total = scoped.groupby("EmployeeName")["OvertimePayBirr"].sum().rename("TotalOvertimePayBirr")
    ot_hours_total = scoped.groupby("EmployeeName")["OvertimeHours"].sum().rename("TotalOvertimeHours")

    # Break out OT pay earned on Sunday / Holiday vs a regular working day —
    # since pay differs, payroll needs to see this split, not just a total.
    sunday_label = tr("day_type_sunday", lang)
    holiday_label = tr("day_type_holiday", lang)
    ot_pay_sunday = (
        scoped[scoped["DayType"] == sunday_label].groupby("EmployeeName")["OvertimePayBirr"].sum().rename("SundayOTPayBirr")
    )
    ot_pay_holiday = (
        scoped[scoped["DayType"] == holiday_label].groupby("EmployeeName")["OvertimePayBirr"].sum().rename("HolidayOTPayBirr")
    )

    summary = (
        pd.concat(
            [
                present_days_equiv,
                sick_count,
                annual_count,
                absent_count,
                ot_hours_total,
                ot_pay_total,
                ot_pay_sunday,
                ot_pay_holiday,
            ],
            axis=1,
        )
        .fillna(0)
        .reset_index()
    )
    summary["TotalPresentDays"] = summary["TotalPresentDays"].round(1)

    st.dataframe(summary, use_container_width=True, hide_index=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(tr("total_present_metric", lang), f"{summary['TotalPresentDays'].sum():.1f}")
    m2.metric(tr("total_ot_hours_metric", lang), f"{summary['TotalOvertimeHours'].sum():.1f} h")
    m3.metric(tr("total_ot_pay_metric", lang), f"{summary['TotalOvertimePayBirr'].sum():,.2f}")
    m4.metric(tr("employees_tracked_metric", lang), len(summary))

    with st.expander(tr("raw_records_expander", lang)):
        st.dataframe(scoped.drop(columns=["_PresentShiftUnits"]), use_container_width=True, hide_index=True)

    st.markdown(f"#### {tr('m2_export_header', lang)}")
    download_buttons(summary, "hr_attendance_overtime_summary", "hr_summary")
    download_buttons(scoped.drop(columns=["_PresentShiftUnits"]), "attendance_raw_records", "hr_raw")
