#!/bin/bash
set -e

echo "========================================================="
echo "   🤖 Auto-Analyst AI — AWS EC2 Production Deploy Script "
echo "========================================================="
echo ""

# ── Color Codes ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SWAP MEMORY (Critical for t2.micro 1GB RAM)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if [ ! -f /swapfile ]; then
    log_info "Creating 2GB Swap Memory..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
    log_ok "Swap memory enabled (2GB)."
else
    log_ok "Swap memory already active."
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. SYSTEM UPDATES & DOCKER INSTALLATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log_info "Installing Docker and dependencies..."
sudo apt-get update -y -qq
sudo apt-get install -y -qq docker.io docker-compose git curl ufw > /dev/null 2>&1

# Start Docker
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER" || true
log_ok "Docker installed and running."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. FIREWALL SETUP (UFW)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log_info "Configuring firewall..."
sudo ufw default deny incoming > /dev/null 2>&1
sudo ufw default allow outgoing > /dev/null 2>&1
sudo ufw allow 22/tcp > /dev/null 2>&1   # SSH
sudo ufw allow 80/tcp > /dev/null 2>&1   # HTTP (Nginx)
sudo ufw --force enable > /dev/null 2>&1
log_ok "Firewall configured: SSH(22) + HTTP(80) allowed."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. ENVIRONMENT CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        log_warn ".env file not found. Creating from .env.example..."
        cp .env.example .env
        log_error "IMPORTANT: Edit .env with your actual API keys before proceeding!"
        echo ""
        echo "  Run:  nano .env"
        echo "  Set:  GROQ_API_KEY, E2B_API_KEY"
        echo ""
        read -p "Press ENTER after editing .env, or Ctrl+C to abort... " -r
    else
        log_error ".env file missing! Create .env with GROQ_API_KEY and E2B_API_KEY."
        exit 1
    fi
fi
log_ok "Environment file ready."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. CREATE DATA DIRECTORIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mkdir -p data/input data/output scripts
log_ok "Data directories created."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. BUILD & LAUNCH DOCKER CONTAINERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log_info "Building and starting Auto-Analyst AI (this may take 3-5 minutes)..."
sudo docker-compose down 2>/dev/null || true
sudo docker-compose up -d --build

# Wait for container to be healthy
log_info "Waiting for services to start..."
sleep 15

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. SYSTEMD SERVICE (Auto-start on boot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log_info "Setting up auto-start on boot..."
APP_DIR=$(pwd)

sudo tee /etc/systemd/system/auto-analyst.service > /dev/null << EOF
[Unit]
Description=Auto-Analyst AI Docker Service
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${APP_DIR}
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable auto-analyst.service > /dev/null 2>&1
log_ok "Auto-start configured (systemd)."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. HEALTH CHECK CRON (Every 5 minutes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log_info "Setting up health check cron..."
chmod +x scripts/health_check.sh 2>/dev/null || true

# Add cron job (avoid duplicates)
CRON_CMD="*/5 * * * * ${APP_DIR}/scripts/health_check.sh >> /var/log/auto-analyst-health.log 2>&1"
(crontab -l 2>/dev/null | grep -v "health_check.sh"; echo "$CRON_CMD") | crontab -
log_ok "Health check cron set (every 5 minutes)."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. VERIFY DEPLOYMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
log_info "Verifying deployment..."

# Check container
if sudo docker ps | grep -q "auto-analyst-ai"; then
    log_ok "Docker container running."
else
    log_error "Container not running! Check: sudo docker-compose logs"
fi

# Check health endpoint
sleep 5
if curl -sf http://localhost/api/health > /dev/null 2>&1; then
    log_ok "API health check passed."
else
    log_warn "API not responding yet. May need more time to start."
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. DEPLOYMENT SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PUBLIC_IP=$(curl -s https://checkip.amazonaws.com 2>/dev/null || curl -s ifconfig.me 2>/dev/null || echo "<YOUR-EC2-PUBLIC-IP>")

echo ""
echo "========================================================="
echo -e "   ${GREEN}🎉 AUTO-ANALYST AI IS NOW LIVE!${NC}"
echo "========================================================="
echo ""
echo -e "   🌐 Web UI:          ${CYAN}http://${PUBLIC_IP}/${NC}"
echo -e "   🔌 API Health:      ${CYAN}http://${PUBLIC_IP}/api/health${NC}"
echo -e "   📄 API Docs:        ${CYAN}http://${PUBLIC_IP}/docs${NC}"
echo ""
echo "========================================================="
echo "   📋 Useful Commands:"
echo "========================================================="
echo "   View logs:        sudo docker-compose logs -f"
echo "   Restart app:      sudo docker-compose restart"
echo "   Stop app:         sudo docker-compose down"
echo "   Rebuild & start:  sudo docker-compose up -d --build"
echo "   Check status:     sudo docker ps"
echo "   Check health:     curl http://localhost/api/health"
echo "========================================================="
echo ""
