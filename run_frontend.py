#!/usr/bin/env python3
"""
Frontend runner script for the Document Analysis Workflow System
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit frontend"""
    try:
        # Change to frontend directory
        frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
        os.chdir(frontend_dir)
        
        print("Starting Document Analysis Workflow Frontend...")
        print("Frontend will be available at: http://localhost:8501")
        print("Make sure the API server is running at: http://localhost:8000")
        print("\nPress Ctrl+C to stop the frontend")
        
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"])
        
    except KeyboardInterrupt:
        print("\nFrontend stopped by user")
    except Exception as e:
        print(f"Error running frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()