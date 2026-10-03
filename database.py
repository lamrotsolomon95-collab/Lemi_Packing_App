"""
database.py
----------------------------------------------------------------------
SQLite Database layer for Lemi National Cement — Packing Department.
Manages users, dispatch records, attendance records, employees, and activity logs.
----------------------------------------------------------------------
"""

import os
import sqlite3
import hashlib
from datetime import datetime, date
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DATA_DIR, "lemi_packing.db")
DISPATCH_CSV = os.path.join(DATA_DIR, "dispatch_data.csv")
ATTENDANCE_CSV = os.path.join(DATA_DIR, "attendance_data.csv")
EMPLOYEES_CSV = os.path.join(DATA_DIR, "employees.csv")

RATE_PER_TON_BIRR = 20.0  # Birr per net ton for manual packaging labor groups


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'worker',
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Dispatch Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dispatch_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        shift TEXT NOT NULL,
        cement_type TEXT NOT NULL,
        dispatch_method TEXT NOT NULL,
        packaging_line TEXT NOT NULL,
        labor_group TEXT NOT NULL,
        truck_plate TEXT NOT NULL,
        trailer_plate TEXT NOT NULL,
        initial_tonnage REAL NOT NULL,
        returned_tonnage REAL NOT NULL,
        net_tonnage REAL NOT NULL,
        penalty_type TEXT NOT NULL,
        penalty_birr REAL NOT NULL,
        penalty_tonnage REAL NOT NULL,
        gross_pay_birr REAL NOT NULL,
        total_penalty_birr REAL NOT NULL,
        net_payable_birr REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Attendance Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        day_type TEXT NOT NULL,
        employee_name TEXT NOT NULL,
        position TEXT NOT NULL,
        day_shift_status TEXT NOT NULL,
        night_shift_status TEXT NOT NULL,
        overtime_hours REAL NOT NULL,
        overtime_rate_birr REAL NOT NULL,
        overtime_pay_birr REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Employees Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT UNIQUE NOT NULL,
        position TEXT NOT NULL
    )
    """)

    # Activity Log Table (Matches Image 1)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT NOT NULL,
        user_email TEXT NOT NULL,
        table_name TEXT NOT NULL,
        action TEXT NOT NULL,
        ref TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed Default Accounts if none exist (using email from screenshot admin@leminationalcementplc.com)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role, status) VALUES (?, ?, ?, ?, ?)",
            ("admin@leminationalcementplc.com", hash_password("admin123"), "Default Administrator", "admin", "active")
        )
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role, status) VALUES (?, ?, ?, ?, ?)",
            ("worker@leminationalcementplc.com", hash_password("work123"), "Packing Worker", "worker", "active")
        )
        conn.commit()

        # Seed initial activity log item matching screenshot
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            "INSERT INTO activity_logs (time, user_email, table_name, action, ref) VALUES (?, ?, ?, ?, ?)",
            (now_str, "admin@leminationalcementplc.com", "dispatch", "create", f"{date.today().strftime('%Y-%m-%d')}/robot")
        )
        conn.commit()

    _migrate_csv_data(conn)
    conn.close()


def log_activity(user_email: str, table_name: str, action: str, ref: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO activity_logs (time, user_email, table_name, action, ref) VALUES (?, ?, ?, ?, ?)",
        (now_str, user_email or "admin@leminationalcementplc.com", table_name, action, ref)
    )
    conn.commit()
    conn.close()


def get_activity_logs(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,))
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return logs


def _migrate_csv_data(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM dispatch_records")
    if cursor.fetchone()[0] == 0 and os.path.exists(DISPATCH_CSV):
        try:
            df = pd.read_csv(DISPATCH_CSV)
            for _, row in df.iterrows():
                p_line = str(row.get("PackagingLine", "N/A"))
                if p_line.startswith("Line "):
                    p_line = p_line.replace("Line ", "Robot ")
                
                l_group = str(row.get("LaborGroup", "N/A"))
                if l_group.startswith("Group "):
                    l_group = l_group.replace("Group ", "Lemi ")

                init_t = float(row.get("InitialLoadedTonnage", 0.0))
                ret_t = float(row.get("ReturnedOverloadTonnage", 0.0))
                net_t = float(row.get("NetTonnage", init_t - ret_t))
                
                pen_type = str(row.get("PenaltyType", "No Penalty"))
                pen_b = float(row.get("PenaltyBirr", 0.0))
                pen_t = float(row.get("PenaltyTonnage", 0.0))
                
                method = str(row.get("DispatchMethod", "robot")).lower()
                is_manual = "manual" in method or "እጅ" in method or "人工" in method
                
                if is_manual:
                    gross = float(row.get("GrossPayBirr", net_t * RATE_PER_TON_BIRR))
                    tot_pen = float(row.get("TotalPenaltyBirr", pen_b + (pen_t * RATE_PER_TON_BIRR)))
                    net_pay = float(row.get("NetPayableBirr", gross - tot_pen))
                else:
                    gross, tot_pen, net_pay = 0.0, 0.0, 0.0

                cursor.execute("""
                INSERT INTO dispatch_records (
                    date, shift, cement_type, dispatch_method, packaging_line, labor_group,
                    truck_plate, trailer_plate, initial_tonnage, returned_tonnage, net_tonnage,
                    penalty_type, penalty_birr, penalty_tonnage, gross_pay_birr, total_penalty_birr, net_payable_birr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(row.get("Date", date.today().strftime("%Y-%m-%d"))),
                    str(row.get("Shift", "N/A")),
                    str(row.get("CementType", "OPC")),
                    str(row.get("DispatchMethod", "Robot Packaging Line")),
                    p_line,
                    l_group,
                    str(row.get("TruckPlateNumber", "  ")),
                    str(row.get("TrailerPlateNumber", "  ")),
                    init_t, ret_t, net_t,
                    pen_type, pen_b, pen_t,
                    gross, tot_pen, net_pay
                ))
            conn.commit()
        except Exception as e:
            pass

    cursor.execute("SELECT COUNT(*) FROM attendance_records")
    if cursor.fetchone()[0] == 0 and os.path.exists(ATTENDANCE_CSV):
        try:
            df = pd.read_csv(ATTENDANCE_CSV)
            for _, row in df.iterrows():
                cursor.execute("""
                INSERT INTO attendance_records (
                    date, day_type, employee_name, position, day_shift_status, night_shift_status,
                    overtime_hours, overtime_rate_birr, overtime_pay_birr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(row.get("Date", date.today().strftime("%Y-%m-%d"))),
                    str(row.get("DayType", "Regular Working Day")),
                    str(row.get("EmployeeName", "")),
                    str(row.get("Position", "Operator")),
                    str(row.get("DayShiftStatus", "✓ Present")),
                    str(row.get("NightShiftStatus", "✓ Present")),
                    float(row.get("OvertimeHours", 0.0)),
                    float(row.get("OvertimeRateBirr", 0.0)),
                    float(row.get("OvertimePayBirr", 0.0))
                ))
            conn.commit()
        except Exception as e:
            pass

    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0 and os.path.exists(EMPLOYEES_CSV):
        try:
            df = pd.read_csv(EMPLOYEES_CSV)
            for _, row in df.iterrows():
                name = str(row.get("FullName", "")).strip()
                pos = str(row.get("Position", "Operator")).strip()
                if name:
                    cursor.execute("INSERT OR IGNORE INTO employees (full_name, position) VALUES (?, ?)", (name, pos))
            conn.commit()
        except Exception as e:
            pass


# --- Calculation Helper ---
def calculate_dispatch_math(dispatch_method: str, initial_tonnage: float, returned_tonnage: float, penalty_type: str, penalty_val: float):
    net_tonnage = max(0.0, initial_tonnage - returned_tonnage)
    is_manual = "manual" in dispatch_method.lower() or "እጅ" in dispatch_method.lower() or "人工" in dispatch_method.lower()

    if is_manual:
        gross_pay = round(net_tonnage * RATE_PER_TON_BIRR, 2)
        penalty_birr = 0.0
        penalty_tonnage = 0.0

        if penalty_type == "birr":
            penalty_birr = round(penalty_val, 2)
        elif penalty_type == "tonnage":
            penalty_tonnage = round(penalty_val, 2)

        total_penalty = round(penalty_birr + (penalty_tonnage * RATE_PER_TON_BIRR), 2)
        net_payable = round(gross_pay - total_penalty, 2)
    else:
        gross_pay = 0.0
        penalty_birr = 0.0
        penalty_tonnage = 0.0
        total_penalty = 0.0
        net_payable = 0.0

    return {
        "net_tonnage": round(net_tonnage, 2),
        "gross_pay_birr": gross_pay,
        "penalty_birr": penalty_birr,
        "penalty_tonnage": penalty_tonnage,
        "total_penalty_birr": total_penalty,
        "net_payable_birr": net_payable
    }


# --- Database CRUD Operations ---

def verify_user(email: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    cursor.execute("SELECT id, email, full_name, role, status FROM users WHERE LOWER(email) = LOWER(?) AND password_hash = ?", (email.strip(), pwd_hash))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None


def change_user_password(user_id: int, old_password: str, new_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    old_hash = hash_password(old_password)
    cursor.execute("SELECT id FROM users WHERE id = ? AND password_hash = ?", (user_id, old_hash))
    if not cursor.fetchone():
        conn.close()
        return False, "Current password is incorrect."
    
    new_hash = hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return True, "Password changed successfully."


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, role, status, created_at FROM users ORDER BY id ASC")
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return users


def create_user(email: str, password: str, full_name: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        cursor.execute("INSERT INTO users (email, password_hash, full_name, role, status) VALUES (?, ?, ?, ?, 'active')",
                       (email.strip(), pwd_hash, full_name.strip(), role))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        log_activity(email, "users", "create", email)
        return True, user_id, "User created successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return False, None, "User with this email already exists."


def update_user_status(user_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE id = ?", (status, user_id))
    conn.commit()
    conn.close()
    return True


def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


# --- Dispatch Operations ---

def save_dispatch_record(data: dict, user_email="admin@leminationalcementplc.com"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    init_t = float(data.get("initial_tonnage", 0.0))
    ret_t = float(data.get("returned_tonnage", 0.0))
    pen_type = str(data.get("penalty_type", "none"))
    pen_val = float(data.get("penalty_value", 0.0))
    method = str(data.get("dispatch_method", "Robot Packaging Line"))

    calc = calculate_dispatch_math(method, init_t, ret_t, pen_type, pen_val)
    d_date = data.get("date", date.today().strftime("%Y-%m-%d"))

    cursor.execute("""
    INSERT INTO dispatch_records (
        date, shift, cement_type, dispatch_method, packaging_line, labor_group,
        truck_plate, trailer_plate, initial_tonnage, returned_tonnage, net_tonnage,
        penalty_type, penalty_birr, penalty_tonnage, gross_pay_birr, total_penalty_birr, net_payable_birr
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d_date,
        data.get("shift", "N/A"),
        data.get("cement_type", "OPC"),
        method,
        data.get("packaging_line", "N/A"),
        data.get("labor_group", "N/A"),
        data.get("truck_plate", "  ").strip().upper() or "  ",
        data.get("trailer_plate", "  ").strip().upper() or "  ",
        init_t, ret_t, calc["net_tonnage"],
        pen_type, calc["penalty_birr"], calc["penalty_tonnage"],
        calc["gross_pay_birr"], calc["total_penalty_birr"], calc["net_payable_birr"]
    ))
    conn.commit()
    rec_id = cursor.lastrowid
    conn.close()

    log_activity(user_email, "dispatch", "create", f"{d_date}/{method.split()[0].lower()}")
    return rec_id, calc


def get_dispatch_records(date_filter=None, shift_filter=None, method_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM dispatch_records WHERE 1=1"
    params = []

    if date_filter:
        query += " AND date = ?"
        params.append(date_filter)
    if shift_filter:
        query += " AND shift = ?"
        params.append(shift_filter)
    if method_filter:
        query += " AND dispatch_method = ?"
        params.append(method_filter)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return records


def delete_dispatch_record(rec_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dispatch_records WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return True


# --- Attendance Operations ---

def save_attendance_batch(records: list, user_email="admin@leminationalcementplc.com"):
    conn = get_db_connection()
    cursor = conn.cursor()

    for r in records:
        emp_name = str(r.get("employee_name", "")).strip()
        pos = str(r.get("position", "")).strip() or "Operator"
        if not emp_name:
            continue

        cursor.execute("INSERT OR IGNORE INTO employees (full_name, position) VALUES (?, ?)", (emp_name, pos))

        ot_hours = float(r.get("overtime_hours", 0.0))
        ot_rate = float(r.get("overtime_rate_birr", 0.0))
        ot_pay = round(ot_hours * ot_rate, 2)
        d_date = r.get("date", date.today().strftime("%Y-%m-%d"))

        cursor.execute("""
        INSERT INTO attendance_records (
            date, day_type, employee_name, position, day_shift_status, night_shift_status,
            overtime_hours, overtime_rate_birr, overtime_pay_birr
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d_date,
            r.get("day_type", "Regular Working Day"),
            emp_name, pos,
            r.get("day_shift_status", "✓ Present"),
            r.get("night_shift_status", "✓ Present"),
            ot_hours, ot_rate, ot_pay
        ))

    conn.commit()
    conn.close()
    log_activity(user_email, "attendance", "batch_create", f"count:{len(records)}")
    return True


def get_attendance_records(date_filter=None, name_filter=None, day_type_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM attendance_records WHERE 1=1"
    params = []

    if date_filter:
        query += " AND date = ?"
        params.append(date_filter)
    if name_filter:
        query += " AND employee_name = ?"
        params.append(name_filter)
    if day_type_filter:
        query += " AND day_type = ?"
        params.append(day_type_filter)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return records


def get_known_employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, position FROM employees ORDER BY full_name ASC")
    emps = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return emps


def delete_attendance_record(rec_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance_records WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return True


# --- Dashboard Analytics Operations ---

def get_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), SUM(net_tonnage), SUM(gross_pay_birr), SUM(total_penalty_birr), SUM(net_payable_birr) FROM dispatch_records")
    d_row = cursor.fetchone()
    total_dispatches = d_row[0] or 0
    total_net_tonnage = round(d_row[1] or 0.0, 2)
    total_labor_gross = round(d_row[2] or 0.0, 2)
    total_penalties = round(d_row[3] or 0.0, 2)
    total_net_labor_pay = round(d_row[4] or 0.0, 2)

    cursor.execute("SELECT COUNT(*), SUM(overtime_hours), SUM(overtime_pay_birr) FROM attendance_records")
    a_row = cursor.fetchone()
    total_attendance_entries = a_row[0] or 0
    total_ot_hours = round(a_row[1] or 0.0, 1)
    total_ot_pay = round(a_row[2] or 0.0, 2)

    cursor.execute("SELECT COUNT(DISTINCT full_name) FROM employees")
    total_employees = cursor.fetchone()[0] or 0

    cursor.execute("""
    SELECT date, SUM(net_tonnage) as daily_tonnage, SUM(net_payable_birr) as daily_pay 
    FROM dispatch_records 
    GROUP BY date 
    ORDER BY date DESC LIMIT 10
    """)
    trend_rows = list(reversed([dict(r) for r in cursor.fetchall()]))

    cursor.execute("""
    SELECT dispatch_method, SUM(net_tonnage) as total_tonnage, COUNT(*) as count 
    FROM dispatch_records 
    GROUP BY dispatch_method
    """)
    method_rows = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
    SELECT labor_group, SUM(net_tonnage) as total_tonnage, SUM(net_payable_birr) as total_pay 
    FROM dispatch_records 
    WHERE labor_group != 'N/A' 
    GROUP BY labor_group
    """)
    group_rows = [dict(r) for r in cursor.fetchall()]

    conn.close()

    logs = get_activity_logs(10)

    return {
        "total_dispatches": total_dispatches,
        "total_net_tonnage": total_net_tonnage,
        "total_labor_gross": total_labor_gross,
        "total_penalties": total_penalties,
        "total_net_labor_pay": total_net_labor_pay,
        "total_attendance_entries": total_attendance_entries,
        "total_ot_hours": total_ot_hours,
        "total_ot_pay": total_ot_pay,
        "total_employees": total_employees,
        "tonnage_trend": trend_rows,
        "method_breakdown": method_rows,
        "group_breakdown": group_rows,
        "activity_logs": logs
    }
