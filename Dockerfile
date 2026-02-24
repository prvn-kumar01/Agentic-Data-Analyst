# ============================================
# Auto-Analyst AI — Streamlit + FastAPI
# ============================================
FROM python:3.11-slim

# Install supervisor, bash, curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends supervisor curl bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY config.py .
COPY server.py .
COPY main.py .
COPY streamlit_app.py .
COPY src/ ./src/
COPY .streamlit/ ./.streamlit/

# Create data directories
RUN mkdir -p data/input data/output

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose FastAPI (internal) — Streamlit uses Render's $PORT
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start both services via supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
