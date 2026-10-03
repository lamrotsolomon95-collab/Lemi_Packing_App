"""
app.py
----------------------------------------------------------------------
Lemi National Cement — Packing Department Application Server (Flask)
----------------------------------------------------------------------
"""

import os
from io import BytesIO
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
import pandas as pd

import database as db
import translations as tr_module
from utils import to_excel_bytes

app = Flask(__name__)
app.secret_key = "lemi_packing_department_secret_key_2026"

# Initialize DB on startup
db.init_db()


# ----------------------------------------------------------------------
# Page Routes
# ----------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ----------------------------------------------------------------------
# Authentication & User Management API
# ----------------------------------------------------------------------
@app.route("/api/translations", methods=["GET"])
def get_translations():
    lang = request.args.get("lang", "en")
    translations_data = {key: tr_module.tr(key, lang) for key in tr_module.T.keys()}
    return jsonify(translations_data)


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = db.verify_user(email, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    if user["status"] == "revoked":
        return jsonify({"success": False, "message": "Your access has been revoked by a supervisor. Please contact administration."}), 403

    session["user"] = user
    return jsonify({"success": True, "user": user, "message": f"Welcome back, {user['full_name']}!"})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True, "message": "Logged out successfully."})


@app.route("/api/auth/current-user", methods=["GET"])
def current_user():
    user = session.get("user", {"id": 0, "email": "", "full_name": "", "role": ""})
    return jsonify({"user": user})


@app.route("/api/auth/change-password", methods=["POST"])
def change_password():
    user = session.get("user")
    if not user or not user.get("id"):
        return jsonify({"success": False, "message": "Please log in first."}), 401

    data = request.json or {}
    old_pwd = data.get("old_password", "")
    new_pwd = data.get("new_password", "")

    if not old_pwd or not new_pwd:
        return jsonify({"success": False, "message": "Both old and new password are required."}), 400

    if len(new_pwd) < 4:
        return jsonify({"success": False, "message": "New password must be at least 4 characters long."}), 400

    success, msg = db.change_user_password(user["id"], old_pwd, new_pwd)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "message": msg}), 400


@app.route("/api/users", methods=["GET"])
def list_users():
    user = session.get("user", {})
    if user.get("role") != "admin":
        return jsonify({"success": False, "message": "Access restricted to Supervisors/Admins."}), 403
    users = db.get_all_users()
    return jsonify({"users": users})


@app.route("/api/users", methods=["POST"])
def add_user():
    user = session.get("user", {})
    if user.get("role") != "admin":
        return jsonify({"success": False, "message": "Access restricted to Supervisors/Admins."}), 403

    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "worker")

    if not email or not password or not full_name:
        return jsonify({"success": False, "message": "Email, password, and full name are required."}), 400

    success, u_id, msg = db.create_user(email, password, full_name, role)
    if success:
        return jsonify({"success": True, "user_id": u_id, "message": msg})
    return jsonify({"success": False, "message": msg}), 400


@app.route("/api/users/<int:user_id>/status", methods=["PUT"])
def update_user_status(user_id):
    user = session.get("user", {})
    if user.get("role") != "admin":
        return jsonify({"success": False, "message": "Access restricted to Supervisors/Admins."}), 403

    data = request.json or {}
    status = data.get("status", "active")
    db.update_user_status(user_id, status)
    return jsonify({"success": True, "message": f"User status updated to {status}."})


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = session.get("user", {})
    if user.get("role") != "admin":
        return jsonify({"success": False, "message": "Access restricted to Supervisors/Admins."}), 403

    if user_id == user.get("id"):
        return jsonify({"success": False, "message": "You cannot delete your own logged-in account."}), 400

    db.delete_user(user_id)
    return jsonify({"success": True, "message": "User deleted."})


# ----------------------------------------------------------------------
# Module 1 — Dispatch API
# ----------------------------------------------------------------------
@app.route("/api/dispatch/calculate", methods=["POST"])
def preview_dispatch_math():
    data = request.json or {}
    method = data.get("dispatch_method", "Robot Packaging Line")
    init_t = float(data.get("initial_tonnage", 0.0))
    ret_t = float(data.get("returned_tonnage", 0.0))
    pen_type = data.get("penalty_type", "none")
    pen_val = float(data.get("penalty_value", 0.0))

    calc = db.calculate_dispatch_math(method, init_t, ret_t, pen_type, pen_val)
    return jsonify(calc)


@app.route("/api/dispatch", methods=["GET"])
def get_dispatch():
    date_filter = request.args.get("date")
    shift_filter = request.args.get("shift")
    method_filter = request.args.get("method")
    records = db.get_dispatch_records(date_filter, shift_filter, method_filter)
    return jsonify({"records": records})


@app.route("/api/dispatch", methods=["POST"])
def save_dispatch():
    data = request.json or {}
    if not data:
        return jsonify({"success": False, "message": "No data provided."}), 400

    rec_id, calc = db.save_dispatch_record(data)
    return jsonify({"success": True, "id": rec_id, "results": calc, "message": "Dispatch record saved successfully."})


@app.route("/api/dispatch/<int:rec_id>", methods=["DELETE"])
def delete_dispatch(rec_id):
    user = session.get("user", {})
    if user.get("role") != "admin":
        return jsonify({"success": False, "message": "Only Supervisors/Admins can delete records."}), 403

    db.delete_dispatch_record(rec_id)
    return jsonify({"success": True, "message": "Record deleted."})


# ----------------------------------------------------------------------
# Module 2 — Attendance API
# ----------------------------------------------------------------------
@app.route("/api/attendance", methods=["GET"])
def get_attendance():
    date_filter = request.args.get("date")
    name_filter = request.args.get("name")
    day_type_filter = request.args.get("day_type")
    records = db.get_attendance_records(date_filter, name_filter, day_type_filter)
    return jsonify({"records": records})


@app.route("/api/attendance", methods=["POST"])
def save_attendance():
    data = request.json or {}
    records = data.get("records", [])

    if not records:
        return jsonify({"success": False, "message": "No attendance records submitted."}), 400

    db.save_attendance_batch(records)
    return jsonify({"success": True, "message": f"Successfully saved attendance for {len(records)} workers."})


@app.route("/api/employees", methods=["GET"])
def get_employees():
    emps = db.get_known_employees()
    return jsonify({"employees": emps})


@app.route("/api/attendance/<int:rec_id>", methods=["DELETE"])
def delete_attendance(rec_id):
    user = session.get("user", {})
    if user.get("role") != "admin":
        return jsonify({"success": False, "message": "Only Supervisors/Admins can delete records."}), 403

    db.delete_attendance_record(rec_id)
    return jsonify({"success": True, "message": "Attendance record deleted."})


# ----------------------------------------------------------------------
# Module 4 — Executive Dashboard API
# ----------------------------------------------------------------------
@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    summary = db.get_dashboard_summary()
    return jsonify(summary)


# ----------------------------------------------------------------------
# Export API (CSV & Excel)
# ----------------------------------------------------------------------
@app.route("/api/export/dispatch", methods=["GET"])
def export_dispatch():
    fmt = request.args.get("format", "csv")
    records = db.get_dispatch_records()
    df = pd.DataFrame(records)

    if df.empty:
        df = pd.DataFrame(columns=["date", "shift", "cement_type", "dispatch_method", "packaging_line", "labor_group", "truck_plate", "trailer_plate", "initial_tonnage", "returned_tonnage", "net_tonnage", "penalty_type", "penalty_birr", "penalty_tonnage", "gross_pay_birr", "total_penalty_birr", "net_payable_birr"])

    if fmt == "excel":
        excel_bytes = to_excel_bytes(df.to_dict(orient="records"), sheet_name="Dispatch_Report")
        return send_file(
            BytesIO(excel_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"lemi_dispatch_report_{date.today().strftime('%Y%m%d')}.xlsx"
        )
    else:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        return send_file(
            BytesIO(csv_bytes),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"lemi_dispatch_report_{date.today().strftime('%Y%m%d')}.csv"
        )


@app.route("/api/export/attendance", methods=["GET"])
def export_attendance():
    fmt = request.args.get("format", "csv")
    records = db.get_attendance_records()
    df = pd.DataFrame(records)

    if df.empty:
        df = pd.DataFrame(columns=["date", "day_type", "employee_name", "position", "day_shift_status", "night_shift_status", "overtime_hours", "overtime_rate_birr", "overtime_pay_birr"])

    if fmt == "excel":
        excel_bytes = to_excel_bytes(df.to_dict(orient="records"), sheet_name="Attendance_Report")
        return send_file(
            BytesIO(excel_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"lemi_attendance_report_{date.today().strftime('%Y%m%d')}.xlsx"
        )
    else:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        return send_file(
            BytesIO(csv_bytes),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"lemi_attendance_report_{date.today().strftime('%Y%m%d')}.csv"
        )


# ----------------------------------------------------------------------
# Run Server
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
