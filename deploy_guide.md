# 🚀 Deployment & Operational Guide
## Lemi National Cement — Packing Workshop System

---

### Option 1: Local Factory PC Deployment (Immediate & Ready Now)

> **No setup or external database needed!**

1. Copy the `Lemi_Packing_Department_App` folder (or unzip `Lemi_Packing_Department_App.zip`) onto the target Windows PC in the Packing Department.
2. Double-click **`run_app.bat`**.
3. The server starts at `http://127.0.0.1:5000` and automatically opens in the web browser.
4. **Access from other PCs on the factory network:**
   - Find the host PC's IP address (e.g. `192.168.1.50`).
   - Other staff can open `http://192.168.1.50:5000` in their browsers on the local network!

---

### Option 2: Docker Container Deployment

1. Build the container:
   ```bash
   docker build -t lemi-packing-app .
   ```
2. Run the container:
   ```bash
   docker run -d -p 5000:5000 --name lemi_packing lemi-packing-app
   ```

---

### Option 3: Cloud Deployment (Render / Railway / AWS / Azure)

1. Upload the project folder or push to GitHub.
2. Set the start command to:
   ```bash
   python app.py
   ```
3. Set Environment Port to `5000`.

---

### Authorized Login Credentials:
- **Supervisor / Admin:** `admin@leminationalcementplc.com` / `admin123`
- **Worker / Data Entry:** `worker@leminationalcementplc.com` / `work123`
