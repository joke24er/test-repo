#!/usr/bin/env python3
"""
Document Analysis Workflow System
Main application entry point
"""

import os
import uvicorn
from dotenv import load_dotenv
from src.api import app

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"Starting Document Analysis Workflow API on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"API Documentation: http://{host}:{port}/docs")
    
    # Run the FastAPI application
    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()