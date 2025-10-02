"""Server startup script"""

import uvicorn

def start_server():
    print("🎵 Starting Groovi Backend Server...")
    print("📡 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()