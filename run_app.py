"""
run_app.py
----------------------------------------------------------------------
One-click python launcher for Lemi Packing Department Web System.
Automatically checks dependencies, launches server & opens browser.
----------------------------------------------------------------------
"""

import sys
import os
import subprocess
import webbrowser
import threading
import time

def check_and_install_dependencies():
    required = ["flask", "pandas", "openpyxl"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Installing missing packages ({', '.join(missing)})... Please wait a moment.")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("Packages installed successfully!\n")

def open_browser():
    time.sleep(1.8)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("=" * 60)
    print("🏭  Lemi National Cement — Packing Department System")
    print("=" * 60)

    check_and_install_dependencies()

    print("Starting Web Application Server at http://127.0.0.1:5000 ...")
    print("Press Ctrl+C to stop the server.\n")

    threading.Thread(target=open_browser, daemon=True).start()

    from app import app
    app.run(host="127.0.0.1", port=5000, debug=False)
