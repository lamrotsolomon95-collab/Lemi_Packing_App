# Lemi National Cement — Packing Department App

A multilingual Streamlit application for the Packing Department, covering:

1. **Module 1 — Dispatch, Tonnage & Labor Group Payment**
2. **Module 2 — HR Attendance, Overtime & Payroll Tracker**

Supports **English / አማርኛ (Amharic) / 中文 (Chinese)** via a sidebar
language selector — every label, button, and header updates dynamically.

## Project Structure

```
lemi_packing_app/
├── app.py                  # Main entry point (language selector + navigation)
├── translations.py         # EN/AM/ZH translation dictionary
├── utils.py                # Shared CSV / Excel / roster helper functions
├── modules/
│   ├── __init__.py
│   ├── dispatch.py         # Module 1 logic & UI (st.fragment-optimized)
│   └── attendance.py       # Module 2 logic & UI (roster CRUD + payroll)
├── employees.csv           # Employee roster (EmployeeID, FullName, Position, BasicSalary)
├── dispatch_data.csv        # Auto-created on first save
├── attendance_data.csv      # Auto-created on first save
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Module 1 — Dispatch Rules & Calculation Engine

Three dispatch methods, each with different conditional logic:

| Method | Shift required? | Truck Plate No. | Trailer/Power Plate No. | Labor Group | Penalty inputs |
|---|---|---|---|---|---|
| Robot Packaging Line | ✅ Yes | ✅ Always visible & writable (optional) | ✅ Always visible & writable (optional) | — | Hidden |
| Manual Packaging Line | ✅ Yes | ✅ Always visible & writable (optional) | ✅ Always visible & writable (optional) | ✅ Group 1–4 | ✅ Shown |
| Bulk Loading | ❌ No | ✅ Always visible & writable (optional) | ✅ Always visible & writable (optional) | — | Hidden |

Both plate fields mirror the factory's real **Daily Dispatch Record
Sheet**, which always captures the truck's own plate *and* its
trailer/power-unit plate — regardless of which line loaded it. Neither
field is restricted by dispatch method; if left blank, it's stored as
two blank spaces (`"  "`).

| Metric | Formula |
|---|---|
| Net Tonnage | Initial Loaded Tonnage − Returned/Overload Tonnage |
| Gross Pay | Net Tonnage × 20 Birr — **Manual Line only**; 0 Birr for Robot & Bulk |
| Total Penalty | Penalty (Birr) + (Penalty (Tonnage) × 20 Birr) — Manual only |
| Net Payable | Gross Pay − Total Penalty |

The Dispatch Method selector and its dependent dropdowns run inside an
`@st.fragment`, so switching between Robot / Manual / Bulk re-renders
only that section — not the whole page — keeping the UI responsive.
Records are saved to `dispatch_data.csv` and can be filtered by date,
shift, and dispatch method, then exported as CSV or Excel.

## Module 2 — One Combined Attendance & Overtime Table

This plant runs 24/7 on two shifts, so attendance is tracked **per
shift** — Shift A (Day) and Shift B (Night), same naming as Module 1 —
using the same status codes used on the factory floor, all inside a
**single editable table**:

| Column | Editable? | Notes |
|---|---|---|
| Employee Name | ✅ | Type directly; add/remove rows freely |
| Position | ✅ | Free text |
| Shift A (Day) | ✅ | `✓ Present` / `R Rest Day` / `SL Sick Leave` / `AL Annual Leave` / `X Absent` |
| Shift B (Night) | ✅ | Same options as Shift A |
| Overtime Hours | ✅ | 0.0–12.0 |
| Overtime Rate (Birr/hr) | ✅ | Entered per employee, per entry |
| Overtime Pay (Birr) | 🔒 auto | Recalculates live as Hours × Rate |

* A **Day Type** selector (Regular / Sunday / Public Holiday) flags
  each entry — auto-suggested from the date, always overridable (see
  below for details).
* Overtime is only counted if the employee was present on at least one
  of the two shifts that day — no OT on a rest/leave/absent day.
* Distinct Name/Position pairs are quietly saved to `employees.csv`
  after each save, so the table pre-fills with known employees next
  time — no separate "Add Employee" step needed.
* After saving, hours/rate/pay reset to 0 for the next entry while
  names & positions are kept.
* The **History / Summary** section is filterable by **both Date and
  Employee Name**, showing present days (as full-day equivalents from
  shift units), sick/annual leave, absences, total OT hours, and total
  OT pay — with a one-click CSV/Excel export for the summary and the
  raw daily records.

### Crash fix: safe filter dropdowns

Every dropdown that lists unique values (dates, shifts, dispatch
methods, employee names, day types) goes through `safe_sorted_unique()`
in `utils.py`, which drops blank/NaN cells and coerces everything to
string before sorting. This prevents the
`TypeError: '<' not supported between instances of 'float' and 'str'`
crash that could occur if a CSV had leftover blank cells from an
earlier version of the app.

### Clean Excel exports (fixes the cramped/overlapping columns)

Every Excel download — dispatch reports, HR summaries, raw records —
now goes through an upgraded `to_excel_bytes()` in `utils.py` that:
* Auto-sizes every column to fit its longest value or header (no more
  headers like `OvertimePayBirr` getting clipped to `OvertimePayBir`).
* Bolds the header row and freezes it, so it stays visible while
  scrolling.

If a column still looks tight, it's because the CSV download was used
instead of Excel — CSV has no formatting control at all (that's a
limitation of the CSV format itself, not this app), so the **Excel
button is the recommended download** for anything you plan to open
and read directly.

### Day Type — because Sunday/Holiday pay is different

Module 2 now has an explicit, visible **Day Type** field next to the
date picker: **Regular Working Day / Sunday / Public Holiday**. It
auto-suggests the correct value from the date (Sunday → "Sunday"), but
you can always override it — useful when a holiday falls on a weekday.
Day Type is saved as its own column on every attendance record (not a
hidden checkbox), is filterable in the History/Summary section, and
the summary table breaks out **Sunday OT Pay** and **Holiday OT Pay**
separately from the overall total, so the pay difference is visible
at a glance.

## Notes for Deployment

* All CSV files are created automatically on first run/save — no
  manual setup required beyond `employees.csv`.
* To reset data, simply delete `dispatch_data.csv` and/or
  `attendance_data.csv`; they will be recreated empty on next save.
