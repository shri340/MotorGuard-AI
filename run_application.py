"""
MotorGuard AI - Production Full-Stack Application Launcher.
Starts FastAPI backend server on port 8000 and Vite preview server on port 5173.
"""

import sys
import os
import subprocess
import time
import webbrowser

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

def launch():
    print("=" * 70)
    print(" MOTORGUARD AI - STARTING FULL-STACK SERVICES")
    print("=" * 70)
    
    # 1. Start FastAPI backend
    print("Starting FastAPI backend server on http://127.0.0.1:8000 ...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=PROJECT_ROOT)
    
    time.sleep(2)
    
    # 2. Start Vite frontend
    print("Starting Vite frontend server on http://localhost:5173 ...")
    frontend_cmd = ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)
    
    print("\n" + "=" * 70)
    print(" MOTORGUARD AI IS RUNNING!")
    print(" -> Frontend Dashboard: http://localhost:5173")
    print(" -> Backend API Docs:   http://127.0.0.1:8000/docs")
    print("=" * 70)
    print("Press Ctrl+C to stop both servers.\n")
    
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("MotorGuard AI stopped.")

if __name__ == "__main__":
    launch()
