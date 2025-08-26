#!/usr/bin/env python3
"""
Startup script for the Document Analysis Workflow System
Runs both API and frontend servers
"""

import subprocess
import sys
import os
import time
import threading
import signal
import requests

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_api():
    """Run the API server"""
    print("🚀 Starting API server...")
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API server failed: {e}")
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")

def run_frontend():
    """Run the frontend server"""
    print("🌐 Starting frontend server...")
    try:
        # Wait for API to be ready
        print("⏳ Waiting for API to be ready...")
        while not check_api_health():
            time.sleep(1)
        print("✅ API is ready!")
        
        # Change to frontend directory and run
        frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
        os.chdir(frontend_dir)
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend server failed: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")

def main():
    """Main startup function"""
    print("📄 Document Analysis Workflow System")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Creating from example...")
        if os.path.exists(".env.example"):
            subprocess.run(["cp", ".env.example", ".env"])
            print("✅ Created .env file. Please edit it with your OpenAI API key.")
            print("   Then run this script again.")
            return
        else:
            print("❌ .env.example not found. Please create a .env file with your OpenAI API key.")
            return
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Give API a moment to start
    time.sleep(2)
    
    # Start frontend
    run_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested")
        print("Shutting down...")