#!/usr/bin/env python3
"""
Simple script to start the FastAPI backend server.
Run this script to start the song recommender backend.
"""

import subprocess
import sys
import os

def start_server():
    """Start the FastAPI server using uvicorn."""
    try:
        print("Starting Song Recommender Backend Server...")
        print("Server will be available at: http://127.0.0.1:8000")
        print("API endpoint: http://127.0.0.1:8000/recommend")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], cwd=os.path.dirname(__file__))
        
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure you have installed the requirements:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    start_server()
