"""
translations.py
----------------------------------------------------------------------
Central translation table for Lemi National Cement — Packing Department.
Supports English (en), Amharic (am), and Chinese (zh).
----------------------------------------------------------------------
"""

from typing import Dict

LANGUAGES: Dict[str, str] = {
    "English": "en",
    "አማርኛ": "am",
    "中文": "zh",
}

T: Dict[str, Dict[str, str]] = {
    # ---------------- App Shell & Headers ----------------
    "app_title": {"en": "Lemi National Cement — Packing Department", "am": "ለሚ ብሔራዊ ሲሚንቶ — የማሸጊያ ክፍል", "zh": "莱米国家水泥厂 — 包装部"},
    "sidebar_company": {"en": "Lemi National Cement Share Company", "am": "ለሚ ብሔራዊ ሲሚንቶ አክሲዮን ማህበር", "zh": "莱米国家水泥股份有限公司"},
    "language_label": {"en": "Language", "am": "ቋንቋ", "zh": "语言"},
    "nav_dashboard": {"en": "📊 Executive Dashboard", "am": "📊 የአመራር ዳሽቦርድ", "zh": "📊 高管仪表盘"},
    "nav_module1": {"en": "📦 Module 1: Packing & Dispatch History", "am": "📦 ሞጁል 1፡ የጭነት እና አላላክ ታሪክ", "zh": "📦 模块一：包装与发货历史"},
    "nav_module2": {"en": "🧑‍🤝‍🧑 Module 2: HR Attendance & Overtime", "am": "🧑‍🤝‍🧑 ሞጁል 2፡ የሠራተኞች መገኘት እና ትርፍ ሰዓት", "zh": "🧑‍🤝‍🧑 模块二：考勤与加班"},
    "nav_module3": {"en": "🛡️ Module 3: Supervisor Access Control", "am": "🛡️ ሞጁል 3፡ የሱፐርቫይዘር መዳረሻ ቁጥጥር", "zh": "🛡️ 模块三：主管权限控制"},
    "login_button": {"en": "🔑 Log In", "am": "🔑 ይግቡ", "zh": "🔑 登录"},
    "logout_button": {"en": "🚪 Log Out", "am": "🚪 ውጣ", "zh": "🚪 退出"},
    "change_password_button": {"en": "🔒 Change Password", "am": "🔒 የይለፍ ቃል ቀይር", "zh": "🔒 修改密码"},
    "user_role_admin": {"en": "Supervisor / Admin", "am": "ሱፐርቫይዘር / አድሚን", "zh": "主管 / 管理员"},
    "user_role_worker": {"en": "Worker / Data Entry", "am": "ሠራተኛ / መረጃ አስገባ", "zh": "员工 / 数据录入员"},

    # ---------------- Module 1: Packing & Dispatch History ----------------
    "m1_title": {"en": "Module 1 — Dispatch, Tonnage & Labor Group Payment", "am": "ሞጁል 1 — አላላክ፣ ቶንዳጅ እና የሠራተኛ ቡድን ክፍያ", "zh": "模块一 — 发货、吨位与班组工资"},
    "m1_subtitle": {"en": "Record daily packaging dispatch, truck details, and calculate manual labor group payments with penalty rules.", "am": "ዕለታዊ የማሸጊያ አላላክ፣ የመኪና መረጃ እና በእጅ ሠራተኞች ክፍያን ከቅጣት ህግጋት ጋር ይመዝግቡ።", "zh": "记录每日包装发货、卡车明细，并根据扣款规则计算人工班组工资。"},
    "dispatch_method_label": {"en": "Dispatch Method", "am": "የአላላክ ዘዴ", "zh": "发货方式"},
    "method_robot": {"en": "Robot Packaging Line", "am": "የሮቦት ማሸጊያ መስመር", "zh": "机器人包装线"},
    "method_manual": {"en": "Manual Packaging Line", "am": "በእጅ የሚሰራ ማሸጊያ መስመር", "zh": "人工包装线"},
    "method_bulk": {"en": "Bulk Loading (Automated Pipe Loading)", "am": "በጅምላ መጫኛ (አውቶማቲክ ቧንቧ መጫኛ)", "zh": "散装装车（自动管道装车）"},
    "packaging_line_label": {"en": "Packaging Line / Machine", "am": "የማሸጊያ መስመር / ማሽን", "zh": "包装线 / 机器"},
    "labor_group_label": {"en": "Manual Labor Group", "am": "በእጅ ሠራተኛ ቡድን", "zh": "人工班组"},
    "date_label": {"en": "Date", "am": "ቀን", "zh": "日期"},
    "shift_label": {"en": "Shift", "am": "ፈረቃ", "zh": "班次"},
    "shift_a": {"en": "Shift A (Day)", "am": "ፈረቃ ሀ (ቀን)", "zh": "白班（A班）"},
    "shift_b": {"en": "Shift B (Night)", "am": "ፈረቃ ለ (ሌሊት)", "zh": "夜班（B班）"},
    "cement_type_label": {"en": "Cement Type", "am": "የሲሚንቶ ዓይነት", "zh": "水泥类型"},
    "truck_plate_label": {"en": "Truck Plate No.", "am": "የመኪና ታርጋ ቁጥር", "zh": "卡车车牌号"},
    "trailer_plate_label": {"en": "Trailer / Power Unit Plate No.", "am": "የተጎታች ተሽከርካሪ ታርጋ ቁጥር", "zh": "挂车/牵引车车牌号"},
    "initial_tonnage_label": {"en": "Initial Loaded Tonnage (tons)", "am": "የመጀመሪያ የተጫነ ቶንዳጅ (ቶን)", "zh": "初始装载吨位（吨）"},
    "returned_tonnage_label": {"en": "Returned / Overload Tonnage (tons)", "am": "የተመለሰ / ትርፍ ጭነት ቶንዳጅ (ቶን)", "zh": "退回/超载吨位（吨）"},
    
    # Penalties & Pay
    "penalty_section_label": {"en": "Penalty Deduction Options", "am": "የቅጣት ቅናሽ አማራጮች", "zh": "扣款选项"},
    "penalty_none": {"en": "No Penalty", "am": "ምንም ቅጣት የለም", "zh": "无扣款"},
    "penalty_birr": {"en": "Penalty in Birr (Flat Amount)", "am": "ቅጣት በብር (መደበኛ መጠን)", "zh": "按比尔扣款（固定金额）"},
    "penalty_tonnage": {"en": "Penalty in Tonnage (Tons × 20 Birr/ton)", "am": "ቅጣት በቶን (ቶን × 20 ብር/ቶን)", "zh": "按吨位扣款（吨位×20比尔/吨）"},
    "penalty_value_label": {"en": "Penalty Value", "am": "የቅጣት መጠን", "zh": "扣款数值"},
    "save_record_button": {"en": "💾 Save Record & Calculate Payment", "am": "💾 መዝግብ እና ክፍያ አስላ", "zh": "💾 保存记录并计算工资"},

    # Live Metrics
    "net_tonnage_metric": {"en": "Net Tonnage", "am": "ተጣራ ቶንዳጅ", "zh": "净吨位"},
    "gross_pay_metric": {"en": "Gross Labor Pay (20 Birr/t)", "am": "ጠቅላላ የሠራተኛ ክፍያ (20 ብር/ቶን)", "zh": "总人工费（20比尔/吨）"},
    "total_penalty_metric": {"en": "Total Penalty Deducted", "am": "ጠቅላላ የተቀነሰ ቅጣት", "zh": "扣款总额"},
    "net_payable_metric": {"en": "Net Payable Amount (Birr)", "am": "ተጣራ ሊከፈል የሚገባው መጠን (ብር)", "zh": "应付净额（比尔）"},

    # Table & Filters
    "breakdown_title": {"en": "Daily Packaging & Dispatch Records", "am": "ዕለታዊ የማሸጊያ እና አላላክ መዝገቦች", "zh": "每日包装与发货记录"},
    "filter_date": {"en": "Filter by Date", "am": "በቀን አጣራ", "zh": "按日期筛选"},
    "filter_shift": {"en": "Filter by Shift", "am": "በፈረቃ አጣራ", "zh": "按班次筛选"},
    "filter_method": {"en": "Filter by Method", "am": "በዘዴ አጣራ", "zh": "按方式筛选"},
    "export_csv": {"en": "⬇️ Export CSV", "am": "⬇️ በ CSV አውርድ", "zh": "⬇️ 导出 CSV"},
    "export_excel": {"en": "⬇️ Export Excel", "am": "⬇️ በ Excel አውርድ", "zh": "⬇️ 导出 Excel"},

    # ---------------- Module 2: HR Attendance & Overtime ----------------
    "m2_title": {"en": "Module 2 — HR Attendance, Overtime & Payroll Tracker", "am": "ሞጁል 2 — የሠራተኞች መገኘት፣ ትርፍ ሰዓት እና ደመወዝ", "zh": "模块二 — 考勤、加班与薪资"},
    "m2_subtitle": {"en": "Track 24/7 Day and Night shift attendance, Sunday/Holiday overtime pay, and employee roster.", "am": "የ 24/7 ቀን እና ሌሊት ፈረቃ መገኘት፣ የእሁድ/በዓል ትርፍ ሰዓት ክፍያ እና የሠራተኞች ዝርዝር ይከታተሉ።", "zh": "跟踪24/7白班和夜班出勤、星期日/节假日加班费及员工名单。"},
    "day_type_label": {"en": "Day Type (Affects Overtime Rate)", "am": "የቀን ዓይነት (የትርፍ ሰዓት ተመንን ይነካል)", "zh": "日期类型（影响加班费率）"},
    "day_type_regular": {"en": "Regular Working Day", "am": "መደበኛ የስራ ቀን", "zh": "常规工作日"},
    "day_type_sunday": {"en": "Sunday", "am": "እሁድ", "zh": "星期日"},
    "day_type_holiday": {"en": "Public Holiday", "am": "የህዝብ በዓል", "zh": "公共假日"},
    "employee_name_label": {"en": "Employee Name", "am": "የሠራተኛ ስም", "zh": "员工姓名"},
    "position_label": {"en": "Position / Job Title", "am": "የስራ መደብ", "zh": "职位 / 岗位"},
    "status_present": {"en": "✓ Present", "am": "✓ ተገኝቷል", "zh": "✓ 出勤"},
    "status_rest": {"en": "R Rest Day", "am": "R የዕረፍት ቀን", "zh": "R 休息日"},
    "status_sick_leave": {"en": "SL Sick Leave", "am": "SL የህመም ፈቃድ", "zh": "SL 病假"},
    "status_annual_leave": {"en": "AL Annual Leave", "am": "AL ዓመታዊ ፈቃድ", "zh": "AL 年假"},
    "status_absent": {"en": "X Absent", "am": "X አልተገኘም", "zh": "X 缺勤"},
    "overtime_hours_label": {"en": "Overtime Hours", "am": "ትርፍ ሰዓት (ሰዓታት)", "zh": "加班小时数"},
    "overtime_rate_label": {"en": "Overtime Rate (Birr/hr)", "am": "የትርፍ ሰዓት ተመን (ብር/ሰዓት)", "zh": "加班费率（比尔/小时）"},
    "overtime_pay_label": {"en": "Overtime Pay (Birr)", "am": "የትርፍ ሰዓት ክፍያ (ብር)", "zh": "加班工资（比尔）"},
    "save_attendance_button": {"en": "💾 Save Shift Attendance", "am": "💾 የፈረቃ መገኘትን መዝግብ", "zh": "💾 保存班次考勤"},
    "add_row_button": {"en": "➕ Add Employee Row", "am": "➕ አዲስ ረድፍ ጨምር", "zh": "➕ 添加员工行"},

    # ---------------- Module 3: Supervisor Access Control ----------------
    "m3_title": {"en": "Module 3 — Supervisor Access Control & User Management", "am": "ሞጁል 3 — የሱፐርቫይዘር መዳረሻ ቁጥጥር እና የተጠቃሚዎች አስተዳደር", "zh": "模块三 — 主管权限控制与用户管理"},
    "m3_subtitle": {"en": "Grant or revoke worker system permissions, create staff logins, and manage roles.", "am": "የሠራተኞችን የመዳረሻ ፈቃድ ይስጡ ወይም ያግዱ፣ አዲስ ተጠቃሚዎችን ይፍጠሩ እና ሚናዎችን ያስተዳድሩ።", "zh": "授予或撤销员工系统权限、创建员工登录账号并管理角色。"},
    "add_user_title": {"en": "Create New User Access", "am": "አዲስ ተጠቃሚ መዳረሻ ፍጠር", "zh": "创建新用户权限"},
    "user_email": {"en": "Email Address", "am": "የኢሜይል አድራሻ", "zh": "电子邮箱"},
    "user_fullname": {"en": "Full Name", "am": "ሙሉ ስም", "zh": "姓名"},
    "user_role": {"en": "System Role", "am": "የስርዓት ሚና", "zh": "系统角色"},
    "user_password": {"en": "Initial Password", "am": "የመጀመሪያ ይለፍ ቃል", "zh": "初始密码"},
    "create_user_button": {"en": "➕ Grant Access / Create Account", "am": "➕ መዳረሻ ስጥ / መለያ ፍጠር", "zh": "➕ 授予权限 / 创建账号"},
    "existing_users_title": {"en": "System Authorized Users Roster", "am": "የተፈቀደላቸው የስርዓቱ ተጠቃሚዎች ዝርዝር", "zh": "系统授权用户名单"},
    "action_revoke": {"en": "🚫 Revoke Access", "am": "🚫 መዳረሻ ከልክል", "zh": "🚫 撤销权限"},
    "action_activate": {"en": "✅ Grant Access", "am": "✅ መዳረሻ ስጥ", "zh": "✅ 恢复权限"},
    "action_delete": {"en": "🗑️ Delete User", "am": "🗑️ ተጠቃሚ ሰርዝ", "zh": "🗑️ 删除用户"},

    # ---------------- Module 4: Dashboard ----------------
    "m4_title": {"en": "Executive Overview & Operations Analytics", "am": "የአመራር ማጠቃለያ እና የክወናዎች ትንተና", "zh": "高管概览与运营分析"},
    "kpi_tonnage": {"en": "Total Net Tonnage", "am": "ጠቅላላ ተጣራ ቶንዳጅ", "zh": "总净吨位"},
    "kpi_labor_pay": {"en": "Net Labor Payroll (Birr)", "am": "ተጣራ የሠራተኛ ደመወዝ (ብር)", "zh": "净人工工资（比尔）"},
    "kpi_penalties": {"en": "Penalties Deducted (Birr)", "am": "የተቀነሱ ቅጣቶች (ብር)", "zh": "已扣除罚款（比尔）"},
    "kpi_ot_pay": {"en": "Total Overtime Pay (Birr)", "am": "ጠቅላላ የትርፍ ሰዓት ክፍያ (ብር)", "zh": "总加班费（比尔）"},
    "kpi_employees": {"en": "Tracked Workers", "am": "የተመዘገቡ ሠራተኞች", "zh": "已登记员工"},
    "chart_tonnage_trend": {"en": "Daily Tonnage Dispatch Trend", "am": "ዕለታዊ የአላላክ ቶንዳጅ አዝማሚያ", "zh": "每日发货吨位趋势"},
    "chart_group_pay": {"en": "Labor Group Tonnage & Pay Breakdown", "am": "የሠራተኛ ቡድን ቶንዳጅ እና ክፍያ ዝርዝር", "zh": "班组吨位与薪资明细"},
}


def tr(key: str, lang: str) -> str:
    """Returns translated string or falls back to English, then key."""
    entry = T.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("en") or key
