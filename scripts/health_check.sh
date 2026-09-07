#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Auto-Analyst AI — Health Check Script
# Runs via cron every 5 minutes
# Auto-restarts container if unhealthy
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
CONTAINER_NAME="auto-analyst-ai"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    echo "[$TIMESTAMP] CRITICAL: Container '$CONTAINER_NAME' is NOT running. Restarting..."
    cd "$APP_DIR" && docker-compose up -d
    echo "[$TIMESTAMP] Container restart initiated."
    exit 1
fi

# Check API health
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost/api/health 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    echo "[$TIMESTAMP] OK: API healthy (HTTP $HTTP_CODE)"
else
    echo "[$TIMESTAMP] WARNING: API returned HTTP $HTTP_CODE. Restarting container..."
    cd "$APP_DIR" && docker-compose restart
    echo "[$TIMESTAMP] Container restart initiated."
fi

# Check disk space (alert if > 85%)
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 85 ]; then
    echo "[$TIMESTAMP] WARNING: Disk usage at ${DISK_USAGE}%! Consider cleanup."
fi

# Check memory usage
MEM_USAGE=$(free | awk '/^Mem:/ {printf "%.0f", $3/$2 * 100}')
if [ "$MEM_USAGE" -gt 90 ]; then
    echo "[$TIMESTAMP] WARNING: Memory usage at ${MEM_USAGE}%!"
fi
