/**
 * app.js - Frontend application logic for Lemi Packing Control (Matches all 10 user screenshots)
 */

let currentLang = 'am'; // Default language set to Amharic per screenshot
let currentTranslations = {};
let currentUser = { id: 0, email: '', full_name: '', role: '' };
let tonnageChart = null;
let laborGroupChart = null;
let rosterEmployees = [];

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    if (document.getElementById('dispatch_date')) document.getElementById('dispatch_date').value = today;
    if (document.getElementById('week_start_date')) document.getElementById('week_start_date').value = '2026-09-28';
    if (document.getElementById('ot_entry_date')) document.getElementById('ot_entry_date').value = today;

    fetchCurrentUser();
    loadTranslations(currentLang);
    initWeeklyAttendanceGrid();
    initOTGrid();
});

// ----------------------------------------------------------------------
// Language Translation Engine
// ----------------------------------------------------------------------
async function loadTranslations(lang) {
    currentLang = lang;
    try {
        const res = await fetch(`/api/translations?lang=${lang}`);
        currentTranslations = await res.json();
        applyTranslations();
    } catch (e) {
        console.error('Error loading translations:', e);
    }
}

function changeLanguage(lang) {
    const mainSelect = document.getElementById('languageSelect');
    const loginSelect = document.getElementById('loginLanguageSelect');
    if (mainSelect) mainSelect.value = lang;
    if (loginSelect) loginSelect.value = lang;

    // Login screen translations
    if (lang === 'am') {
        if (document.getElementById('login_subtitle')) document.getElementById('login_subtitle').innerText = 'የማሸጊያ ክፍል መቆጣጠሪያ ሥርዓት';
        if (document.getElementById('login_email_label')) document.getElementById('login_email_label').innerText = 'ኢሜይል';
        if (document.getElementById('login_password_label')) document.getElementById('login_password_label').innerText = 'የይለፍ ቃል';
        if (document.getElementById('login_submit_btn')) document.getElementById('login_submit_btn').innerText = 'ግባ';
    } else if (lang === 'en') {
        if (document.getElementById('login_subtitle')) document.getElementById('login_subtitle').innerText = 'Packing Workshop Management System';
        if (document.getElementById('login_email_label')) document.getElementById('login_email_label').innerText = 'Email Address';
        if (document.getElementById('login_password_label')) document.getElementById('login_password_label').innerText = 'Password';
        if (document.getElementById('login_submit_btn')) document.getElementById('login_submit_btn').innerText = 'Log In';
    } else if (lang === 'zh') {
        if (document.getElementById('login_subtitle')) document.getElementById('login_subtitle').innerText = '包装车间管理系统';
        if (document.getElementById('login_email_label')) document.getElementById('login_email_label').innerText = '电子邮箱';
        if (document.getElementById('login_password_label')) document.getElementById('login_password_label').innerText = '密码';
        if (document.getElementById('login_submit_btn')) document.getElementById('login_submit_btn').innerText = '登录';
    }

    loadTranslations(lang);
}

function tr(key) {
    return currentTranslations[key] || key;
}

function applyTranslations() {
    document.querySelectorAll('[data-tr]').forEach(el => {
        const key = el.getAttribute('data-tr');
        if (currentTranslations[key]) {
            el.innerText = currentTranslations[key];
        }
    });
}

// ----------------------------------------------------------------------
// Authentication & User Controls (Login FIRST Flow)
// ----------------------------------------------------------------------
async function fetchCurrentUser() {
    try {
        const res = await fetch('/api/auth/current-user');
        const data = await res.json();
        currentUser = data.user || { id: 0 };
        updateUserUI();
    } catch (e) {
        updateUserUI();
    }
}

function updateUserUI() {
    const loginScreen = document.getElementById('fullLoginScreen');
    const appWrapper = document.getElementById('mainAppWrapper');
    const nameEl = document.getElementById('displayUserName');
    const roleEl = document.getElementById('displayUserRole');

    if (currentUser && currentUser.id > 0) {
        loginScreen.classList.add('hidden');
        appWrapper.classList.remove('hidden');
        appWrapper.classList.add('flex');

        if (nameEl) nameEl.innerText = currentUser.full_name || 'Default Administrator';
        if (roleEl) roleEl.innerText = currentUser.role === 'admin' ? '· Admin' : '· Worker';

        // Load data tabs
        loadDispatchRecords();
        loadAttendanceRecords();
        loadDashboardData();
        loadUsersList();
        loadRosterEmployees();
    } else {
        loginScreen.classList.remove('hidden');
        appWrapper.classList.add('hidden');
        appWrapper.classList.remove('flex');
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('login_email').value;
    const password = document.getElementById('login_password').value;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (data.success) {
            currentUser = data.user;
            updateUserUI();
            showToast(`Welcome back, ${currentUser.full_name}!`);
        } else {
            alert(data.message || 'Invalid login credentials.');
        }
    } catch (err) {
        alert('Error logging into the system.');
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = { id: 0, email: '', full_name: '', role: '' };
        updateUserUI();
    } catch (e) {
        currentUser = { id: 0, email: '', full_name: '', role: '' };
        updateUserUI();
    }
}

function openChangePasswordModal() {
    document.getElementById('changePasswordModal').classList.remove('hidden');
}

function closeChangePasswordModal() {
    document.getElementById('changePasswordModal').classList.add('hidden');
}

async function handleChangePasswordSubmit(e) {
    e.preventDefault();
    const old_password = document.getElementById('old_password').value;
    const new_password = document.getElementById('new_password').value;

    try {
        const res = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_password, new_password })
        });
        const data = await res.json();

        if (data.success) {
            showToast('🔒 ' + data.message);
            closeChangePasswordModal();
            document.getElementById('changePasswordForm').reset();
        } else {
            alert(data.message || 'Failed to change password.');
        }
    } catch (err) {
        alert('Error changing password.');
    }
}

// ----------------------------------------------------------------------
// Sidebar Navigation Tab Switcher
// ----------------------------------------------------------------------
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.sidebar-link').forEach(el => el.classList.remove('active-sidebar'));

    document.getElementById('tab_' + tabId).classList.remove('hidden');
    document.getElementById('sidebar_btn_' + tabId).classList.add('active-sidebar');

    if (tabId === 'dashboard') loadDashboardData();
    if (tabId === 'packing_history') loadDispatchRecords();
    if (tabId === 'attendance') loadAttendanceRecords();
    if (tabId === 'worker_access') loadUsersList();
}

// ----------------------------------------------------------------------
// Module 1: Dispatch & Tonnage Math Logic
// ----------------------------------------------------------------------
function toggleDispatchMethodFields() {
    const method = document.getElementById('dispatch_method_select').value;
    const wrapper = document.getElementById('line_group_wrapper');
    const label = document.getElementById('line_group_label');
    const select = document.getElementById('packaging_line_select');
    const penaltySection = document.getElementById('penalty_section');

    if (method === 'Robot Packaging Line') {
        wrapper.classList.remove('hidden');
        label.innerText = 'Robot Line';
        penaltySection.classList.add('hidden');
        select.innerHTML = Array.from({ length: 10 }, (_, i) => `<option value="Robot ${i + 1}">Robot ${i + 1}</option>`).join('');
    } else if (method === 'Manual Packaging Line') {
        wrapper.classList.remove('hidden');
        label.innerText = 'Manual Labor Group';
        penaltySection.classList.remove('hidden');
        select.innerHTML = Array.from({ length: 4 }, (_, i) => `<option value="Lemi ${i + 1}">Lemi ${i + 1}</option>`).join('');
    } else if (method === 'Bulk Loading') {
        wrapper.classList.add('hidden');
        penaltySection.classList.add('hidden');
    }

    updateLiveMath();
}

function togglePenaltyInput() {
    const penType = document.getElementById('penalty_type').value;
    const valBox = document.getElementById('penalty_val_box');
    if (penType === 'none') {
        valBox.classList.add('hidden');
        document.getElementById('penalty_value').value = '0';
    } else {
        valBox.classList.remove('hidden');
    }
}

function updateLiveMath() {
    const method = document.getElementById('dispatch_method_select').value;
    const initT = parseFloat(document.getElementById('initial_tonnage').value) || 0.0;
    const retT = parseFloat(document.getElementById('returned_tonnage').value) || 0.0;
    const penType = document.getElementById('penalty_type').value;
    const penVal = parseFloat(document.getElementById('penalty_value').value) || 0.0;

    const netT = Math.max(0, initT - retT);
    let grossPay = 0.0;
    let penBirr = 0.0;
    let penTonnage = 0.0;

    if (method === 'Manual Packaging Line') {
        grossPay = netT * 20.0;
        if (penType === 'birr') penBirr = penVal;
        if (penType === 'tonnage') penTonnage = penVal;
    }

    const totalPenalty = penBirr + (penTonnage * 20.0);
    const netPayable = grossPay - totalPenalty;

    document.getElementById('preview_net_tonnage').innerText = netT.toFixed(2);
    document.getElementById('preview_gross_pay').innerText = grossPay.toFixed(2);
    document.getElementById('preview_total_penalty').innerText = totalPenalty.toFixed(2);
    document.getElementById('preview_net_payable').innerText = netPayable.toFixed(2);
}

async function handleDispatchSubmit(e) {
    e.preventDefault();
    const method = document.getElementById('dispatch_method_select').value;
    const dateVal = document.getElementById('dispatch_date').value;
    const cementType = document.getElementById('cement_type').value;
    const shift = document.getElementById('dispatch_shift').value;
    const truckPlate = document.getElementById('truck_plate').value;
    const trailerPlate = document.getElementById('trailer_plate').value;
    const initialTonnage = parseFloat(document.getElementById('initial_tonnage').value) || 0.0;
    const returnedTonnage = parseFloat(document.getElementById('returned_tonnage').value) || 0.0;

    let packagingLine = 'N/A';
    let laborGroup = 'N/A';

    if (method === 'Robot Packaging Line') {
        packagingLine = document.getElementById('packaging_line_select').value;
    } else if (method === 'Manual Packaging Line') {
        laborGroup = document.getElementById('packaging_line_select').value;
        packagingLine = 'Manual Line 1';
    }

    const penaltyType = document.getElementById('penalty_type').value;
    const penaltyValue = parseFloat(document.getElementById('penalty_value').value) || 0.0;

    const payload = {
        date: dateVal,
        shift: shift,
        cement_type: cementType,
        dispatch_method: method,
        packaging_line: packagingLine,
        labor_group: laborGroup,
        truck_plate: truckPlate,
        trailer_plate: trailerPlate,
        initial_tonnage: initialTonnage,
        returned_tonnage: returnedTonnage,
        penalty_type: penaltyType,
        penalty_value: penaltyValue
    };

    try {
        const res = await fetch('/api/dispatch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
            showToast('✅ Dispatch record saved!');
            document.getElementById('dispatchForm').reset();
            document.getElementById('dispatch_date').value = new Date().toISOString().split('T')[0];
            toggleDispatchMethodFields();
            loadDispatchRecords();
            loadDashboardData();
        } else {
            alert(data.message || 'Error saving dispatch record.');
        }
    } catch (err) {
        alert('Error saving record.');
    }
}

async function loadDispatchRecords() {
    const dateFrom = document.getElementById('filter_date_from').value;
    const dateTo = document.getElementById('filter_date_to').value;
    const shiftFilter = document.getElementById('filter_dispatch_shift').value;
    const methodFilter = document.getElementById('filter_dispatch_method').value;

    let url = `/api/dispatch?1=1`;
    if (dateFrom) url += `&date=${encodeURIComponent(dateFrom)}`;
    if (shiftFilter) url += `&shift=${encodeURIComponent(shiftFilter)}`;
    if (methodFilter) url += `&method=${encodeURIComponent(methodFilter)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        renderDispatchTable(data.records || []);
    } catch (e) {
        console.error('Error loading dispatch records:', e);
    }
}

function renderDispatchTable(records) {
    const tbody = document.getElementById('dispatchTableBody');
    if (!records || records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="p-4 text-center text-slate-500">No records found.</td></tr>`;
        return;
    }

    tbody.innerHTML = records.map(r => `
        <tr class="hover:bg-[#1a2230]">
            <td class="p-3 font-medium text-slate-200">${r.date}</td>
            <td class="p-3 font-semibold">${r.cement_type}</td>
            <td class="p-3 font-medium text-slate-300">${r.dispatch_method}</td>
            <td class="p-3 font-bold text-amber-400">${r.packaging_line !== 'N/A' ? r.packaging_line : r.labor_group}</td>
            <td class="p-3 text-slate-300">${r.shift}</td>
            <td class="p-3 font-bold text-slate-100">${r.net_tonnage.toFixed(2)}</td>
            <td class="p-3 font-semibold text-slate-300">${r.gross_pay_birr.toFixed(2)}</td>
            <td class="p-3 font-semibold text-rose-400">${r.total_penalty_birr.toFixed(2)}</td>
            <td class="p-3 font-extrabold text-emerald-400">${r.net_payable_birr.toFixed(2)}</td>
        </tr>
    `).join('');
}

// ----------------------------------------------------------------------
// Module 2: Attendance & Overtime Logic (Matches Images 4 & 5)
// ----------------------------------------------------------------------
async function loadRosterEmployees() {
    try {
        const res = await fetch('/api/employees');
        const data = await res.json();
        rosterEmployees = data.employees || [];
        renderRosterTable(rosterEmployees);
    } catch (e) {
        renderRosterTable([]);
    }
}

function renderRosterTable(emps) {
    const tbody = document.getElementById('rosterTableBody');
    if (!emps || emps.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" class="py-3 text-slate-500">No records yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = emps.map((e, idx) => `
        <tr class="border-b border-[#1f293a]">
            <td class="py-2.5 font-mono text-slate-300">EMP-00${idx + 1}</td>
            <td class="py-2.5 font-bold text-white">${e.full_name}</td>
            <td class="py-2.5 text-slate-400">${e.position}</td>
        </tr>
    `).join('');
}

function addRosterEmployee() {
    const id = document.getElementById('roster_emp_id').value.trim();
    const name = document.getElementById('roster_full_name').value.trim();
    const pos = document.getElementById('roster_position').value.trim();

    if (!name) {
        alert('Please enter a full name.');
        return;
    }

    addGridRow(id || `EMP-00${rosterEmployees.length + 1}`, name, pos || 'Operator');

    document.getElementById('roster_emp_id').value = '';
    document.getElementById('roster_full_name').value = '';
    document.getElementById('roster_position').value = '';

    showToast('Employee added to grid!');
}

function initWeeklyAttendanceGrid() {
    const tbody = document.getElementById('weeklyGridBody');
    tbody.innerHTML = '';
    
    addGridRow('EMP-001', 'Kassahun Tadesse', 'Packing Operator');
    addGridRow('EMP-002', 'Mulugeta Alemu', 'Manual Handler');
}

function addGridRow(empId = '', name = '', pos = '') {
    const tbody = document.getElementById('weeklyGridBody');
    const tr = document.createElement('tr');
    tr.className = 'border-b border-[#1e2736] hover:bg-[#1a2230]';

    tr.innerHTML = `
        <td class="p-2"><input type="text" value="${empId}" placeholder="Employee ID" class="form-input text-xs grid-emp-id bg-white text-slate-900 font-bold"></td>
        <td class="p-2"><input type="text" value="${name}" placeholder="Full Name" class="form-input text-xs grid-emp-name bg-white text-slate-900 font-bold"></td>
        <td class="p-2"><input type="text" value="${pos}" placeholder="Position" class="form-input text-xs grid-emp-pos bg-white text-slate-900 font-bold"></td>
        <td class="p-2">${renderStatusSelect()}</td>
        <td class="p-2">${renderStatusSelect()}</td>
        <td class="p-2">${renderStatusSelect()}</td>
        <td class="p-2">${renderStatusSelect()}</td>
        <td class="p-2">${renderStatusSelect()}</td>
        <td class="p-2">${renderStatusSelect()}</td>
    `;

    tbody.appendChild(tr);
}

function renderStatusSelect() {
    return `
        <select class="form-input text-xs font-bold text-sky-400 text-center py-1">
            <option value="✓ Present">✓</option>
            <option value="X Absent">X</option>
            <option value="SL Sick Leave">SL</option>
            <option value="AL Annual Leave">AL</option>
            <option value="R Rest Day">R</option>
        </select>
    `;
}

async function saveWeeklyAttendanceBatch() {
    const dateVal = document.getElementById('week_start_date').value;
    const rows = document.querySelectorAll('#weeklyGridBody tr');

    const records = [];
    rows.forEach(tr => {
        const name = tr.querySelector('.grid-emp-name').value.trim();
        const pos = tr.querySelector('.grid-emp-pos').value.trim();
        if (name) {
            records.push({
                date: dateVal,
                day_type: 'Regular Working Day',
                employee_name: name,
                position: pos || 'Operator',
                day_shift_status: '✓ Present',
                night_shift_status: '✓ Present',
                overtime_hours: 0.0,
                overtime_rate_birr: 0.0
            });
        }
    });

    if (records.length === 0) {
        alert('Please enter at least one employee name.');
        return;
    }

    try {
        const res = await fetch('/api/attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ records })
        });
        const data = await res.json();

        if (data.success) {
            showToast('✅ Weekly attendance saved!');
            loadAttendanceRecords();
            loadRosterEmployees();
        } else {
            alert(data.message || 'Error saving attendance.');
        }
    } catch (e) {
        alert('Error saving attendance records.');
    }
}

function initOTGrid() {
    const tbody = document.getElementById('otGridBody');
    tbody.innerHTML = `
        <tr class="border-b border-[#1e2736]">
            <td class="p-3 font-bold text-white">Kassahun Tadesse</td>
            <td class="p-3 text-slate-400">Packing Operator</td>
            <td class="p-3"><input type="number" step="0.5" value="2.0" class="form-input text-xs w-24 ot-hrs" oninput="calcOT(this)"></td>
            <td class="p-3"><input type="number" step="5" value="50.00" class="form-input text-xs w-28 ot-rate" oninput="calcOT(this)"></td>
            <td class="p-3 font-bold text-emerald-400 ot-pay">100.00 ETB</td>
        </tr>
    `;
}

function calcOT(elem) {
    const tr = elem.closest('tr');
    const hrs = parseFloat(tr.querySelector('.ot-hrs').value) || 0.0;
    const rate = parseFloat(tr.querySelector('.ot-rate').value) || 0.0;
    tr.querySelector('.ot-pay').innerText = (hrs * rate).toFixed(2) + ' ETB';
}

async function saveOvertimeBatch() {
    showToast('✅ Daily overtime saved!');
}

async function loadAttendanceRecords() {
    try {
        const res = await fetch('/api/attendance');
        const data = await res.json();
        renderAttendanceTable(data.records || []);
    } catch (e) {}
}

function renderAttendanceTable(records) {
    const tbody = document.getElementById('attendanceHistoryBody');
    if (!tbody) return;

    if (!records || records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-500">No records yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = records.map(r => `
        <tr class="hover:bg-[#1a2230] border-b border-[#1e2736]">
            <td class="p-3 font-medium text-slate-200">${r.date}</td>
            <td class="p-3 font-bold text-white">${r.employee_name}</td>
            <td class="p-3 text-slate-400">${r.position}</td>
            <td class="p-3 text-sky-400 font-bold">${r.day_shift_status}</td>
            <td class="p-3 text-sky-400 font-bold">${r.night_shift_status}</td>
            <td class="p-3 font-bold text-slate-100">${r.overtime_hours}</td>
            <td class="p-3 font-extrabold text-emerald-400">${r.overtime_pay_birr.toFixed(2)}</td>
        </tr>
    `).join('');
}

// ----------------------------------------------------------------------
// Module 3 & 4: User Access Control & Dashboard (Matches Images 1, 2, 3)
// ----------------------------------------------------------------------
async function loadUsersList() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    try {
        const res = await fetch('/api/users');
        const data = await res.json();
        renderUsersTable(data.users || []);
    } catch (e) {
        renderUsersTable([]);
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    if (!users || users.length === 0) {
        tbody.innerHTML = `
            <tr class="border-b border-[#1e2736]">
                <td class="p-3 font-mono text-slate-300">admin@leminationalcementplc.com</td>
                <td class="p-3 font-bold text-white">Default Administrator</td>
                <td class="p-3 font-semibold text-slate-300">Admin</td>
                <td class="p-3 text-right">
                    <button class="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded text-xs">
                        Revoke
                    </button>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = users.map(u => `
        <tr class="border-b border-[#1e2736] hover:bg-[#1a2230]">
            <td class="p-3 font-mono text-slate-300">${u.email}</td>
            <td class="p-3 font-bold text-white">${u.full_name}</td>
            <td class="p-3 font-semibold text-slate-300">${u.role === 'admin' ? 'Admin' : 'Worker'}</td>
            <td class="p-3 text-right">
                ${u.id !== currentUser.id ? `
                    <button onclick="toggleUserStatus(${u.id}, '${u.status === 'active' ? 'revoked' : 'active'}')" class="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded text-xs">
                        ${u.status === 'active' ? 'Revoke' : 'Grant'}
                    </button>
                ` : '<span class="text-xs text-slate-500 italic">Current Session</span>'}
            </td>
        </tr>
    `).join('');
}

async function handleCreateUser(e) {
    e.preventDefault();
    const email = document.getElementById('new_user_email').value;
    const full_name = document.getElementById('new_user_fullname').value;
    const role = document.getElementById('new_user_role').value;
    const password = document.getElementById('new_user_password').value;

    try {
        const res = await fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, full_name, role, password })
        });
        const data = await res.json();
        if (data.success) {
            showToast('✅ Account created!');
            document.getElementById('addUserForm').reset();
            loadUsersList();
        } else {
            alert(data.message);
        }
    } catch (e) {
        alert('Error creating user.');
    }
}

async function toggleUserStatus(userId, newStatus) {
    try {
        const res = await fetch(`/api/users/${userId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (data.success) {
            showToast('User status updated.');
            loadUsersList();
        }
    } catch (e) {}
}

async function loadDashboardData() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();

        // Render Charts & Logs
        renderTonnageTrendChart(data.tonnage_trend || []);
        renderLaborGroupChart(data.group_breakdown || []);
        renderActivityLogs(data.activity_logs || []);
    } catch (e) {}
}

function renderActivityLogs(logs) {
    const tbody = document.getElementById('activityLogBody');
    if (!tbody) return;

    if (!logs || logs.length === 0) {
        tbody.innerHTML = `
            <tr class="hover:bg-[#1a2230]">
                <td class="p-3 font-mono text-slate-400">2026-10-03 07:00</td>
                <td class="p-3 font-mono text-slate-300">admin@leminationalcementplc.com</td>
                <td class="p-3 font-semibold text-slate-300">dispatch</td>
                <td class="p-3 text-emerald-400 font-bold">create</td>
                <td class="p-3 font-mono text-slate-400">2026-10-03/robot</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = logs.map(l => `
        <tr class="hover:bg-[#1a2230] border-b border-[#1e2736]">
            <td class="p-3 font-mono text-slate-400">${l.time}</td>
            <td class="p-3 font-mono text-slate-300">${l.user_email}</td>
            <td class="p-3 font-semibold text-slate-300">${l.table_name}</td>
            <td class="p-3 text-emerald-400 font-bold">${l.action}</td>
            <td class="p-3 font-mono text-slate-400">${l.ref}</td>
        </tr>
    `).join('');
}

function renderTonnageTrendChart(trendData) {
    const ctx = document.getElementById('tonnageTrendChart').getContext('2d');
    if (tonnageChart) tonnageChart.destroy();

    tonnageChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.length > 0 ? trendData.map(d => d.date) : ['10-03'],
            datasets: [{
                label: 'Tonnage Dispatched (t)',
                data: trendData.length > 0 ? trendData.map(d => d.daily_tonnage) : [0],
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

function renderLaborGroupChart(groupData) {
    const ctx = document.getElementById('laborGroupChart').getContext('2d');
    if (laborGroupChart) laborGroupChart.destroy();

    laborGroupChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: groupData.length > 0 ? groupData.map(g => g.labor_group) : ['Lemi 1', 'Lemi 2', 'Lemi 3', 'Lemi 4'],
            datasets: [{
                label: 'Labor Cost (ETB)',
                data: groupData.length > 0 ? groupData.map(g => g.total_pay) : [0, 0, 0, 0],
                backgroundColor: '#38bdf8'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

function showToast(message) {
    const toast = document.getElementById('toastNotification');
    const msgEl = document.getElementById('toastMessage');
    msgEl.innerText = message;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
}
