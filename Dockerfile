
FROM python:3.11-slim

# Install supervisor, nginx, bash, curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        supervisor curl bash nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies (cached layer — only rebuilds when requirements change)
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

# Copy Nginx config
COPY nginx.conf /etc/nginx/sites-available/default
RUN rm -f /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose only port 80 (Nginx handles everything)
EXPOSE 80

# Health check via Nginx
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# Start all services via supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
