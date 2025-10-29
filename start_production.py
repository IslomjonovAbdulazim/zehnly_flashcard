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
    
    # Railway-optimized single worker for better database connection handling
    port = os.environ.get("PORT", "8000")
    
    if use_gunicorn:
        cmd = [
            "gunicorn", 
            "app.main:app", 
            "-w", "1",  # Single worker for Railway
            "-k", "uvicorn.workers.UvicornWorker",
            "--bind", f"0.0.0.0:{port}",
            "--timeout", "30",
            "--access-logfile", "-",
            "--error-logfile", "-"
        ]
        print("🚀 Starting with Gunicorn (1 worker - Railway optimized)...")
    else:
        cmd = [
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", port, 
            "--workers", "1",  # Single worker for Railway
            "--timeout-keep-alive", "30"
        ]
        print("🚀 Starting with Uvicorn (1 worker - Railway optimized)...")
    
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