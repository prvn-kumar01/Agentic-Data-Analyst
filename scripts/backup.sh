#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Auto-Analyst AI — Backup Script
# Backs up data directory and config files
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${APP_DIR}/backups"

mkdir -p "$BACKUP_DIR"

echo "🔄 Starting backup at $(date)..."

# Backup data directory
if [ -d "${APP_DIR}/data" ]; then
    tar -czf "${BACKUP_DIR}/data_backup_${TIMESTAMP}.tar.gz" -C "${APP_DIR}" data/
    echo "✅ Data directory backed up."
fi

# Backup config files
tar -czf "${BACKUP_DIR}/config_backup_${TIMESTAMP}.tar.gz" \
    -C "${APP_DIR}" \
    .env.example \
    docker-compose.yml \
    Dockerfile \
    nginx.conf \
    supervisord.conf \
    requirements.txt \
    2>/dev/null
echo "✅ Config files backed up."

# Cleanup old backups (keep last 5)
cd "$BACKUP_DIR"
ls -t data_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
ls -t config_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null

echo "✅ Backup complete. Files in: ${BACKUP_DIR}"
ls -lh "$BACKUP_DIR"
