#!/usr/bin/env python3
"""
Production startup script for FastAPI application.
"""
import os
import subprocess
import sys

def main():
    """Start the FastAPI application in production mode."""
    
    # Set production environment
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "false"
    
    # Check if gunicorn is available
    try:
        subprocess.check_call([sys.executable, "-c", "import gunicorn"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        use_gunicorn = True
    except (subprocess.CalledProcessError, ImportError):
        use_gunicorn = False
        print("⚠️  Gunicorn not found. Using uvicorn directly.")
        print("   For better production performance, install gunicorn:")
        print("   pip install gunicorn")
    
    # Production command
    if use_gunicorn:
        cmd = [
            "gunicorn", 
            "app.main:app", 
            "-w", "4",
            "-k", "uvicorn.workers.UvicornWorker",
            "--bind", "0.0.0.0:8000",
            "--access-logfile", "-",
            "--error-logfile", "-"
        ]
        print("🚀 Starting with Gunicorn (4 workers)...")
    else:
        cmd = [
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--workers", "4"
        ]
        print("🚀 Starting with Uvicorn (4 workers)...")
    
    print("🌐 Server will be available at: http://0.0.0.0:8000")
    print("📖 API docs will be available at: http://0.0.0.0:8000/docs")
    print("🔧 Environment: production")
    print("⚙️  Debug: disabled")
    print()
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()