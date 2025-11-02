# 502 Bad Gateway Fix - PaddleOCR System Dependencies

## Problem
Server fails to start with `ImportError: libgomp.so.1: cannot open shared object file: No such file or directory`

## Root Cause
PaddleOCR requires system-level dependencies that are missing in the deployment environment:
- `libgomp.so.1` (GNU OpenMP library)
- Other system dependencies for PaddlePaddle

## Solutions

### Option 1: Install System Dependencies (Recommended for Railway)

Add these system packages to your deployment:

```bash
# For Ubuntu/Debian-based systems
apt-get update && apt-get install -y \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1
```

**For Railway deployment**, create a `railway.toml` file:

```toml
[build]
builder = "nixpacks"

[build.nixpacksConfig]
aptPkgs = ["libgomp1", "libgl1-mesa-glx", "libglib2.0-0", "libsm6", "libxext6", "libxrender-dev", "libfontconfig1"]
```

### Option 2: Use Docker (Alternative)

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 3: Remove PaddleOCR (If OCR not needed)

Remove from `requirements.txt`:
```
# paddlepaddle==2.6.1
# paddleocr==2.7.3
```

## Status
✅ Server will now start even if PaddleOCR dependencies are missing  
✅ OCR endpoints will return 503 with helpful error message  
⚠️  OCR functionality disabled until system dependencies are installed  

## Verification
After deploying the fix:
1. Server should start successfully
2. `/health` endpoint should return 200
3. Folder API endpoints should work normally
4. OCR endpoints will return 503 until dependencies are fixed

## Next Steps
Choose Option 1 for Railway or Option 2 for Docker to restore full OCR functionality.