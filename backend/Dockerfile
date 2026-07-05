# Doc2Draw backend image (guide §8.1).
# IMPORTANT: build with the REPO ROOT as context so the `doc2draw` core package
# (which lives one level above backend/) is included:
#   docker build -f backend/Dockerfile -t doc2draw-backend .
FROM python:3.11-slim

WORKDIR /app

# System deps required for OpenCV video parsing & PDF/image tooling.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the core engine and backend app (mirrors the repo layout so
# `import doc2draw` and `backend.app.main` both resolve).
COPY doc2draw ./doc2draw
COPY setup.py ./setup.py
COPY backend ./backend

EXPOSE 8000

# Start the FastAPI server. Override with the Celery command for the worker.
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
