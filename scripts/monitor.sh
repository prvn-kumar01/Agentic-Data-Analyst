#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Auto-Analyst AI — System Monitor
# Quick system status overview
# Usage: ./scripts/monitor.sh
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "========================================================="
echo -e "   ${CYAN}🤖 Auto-Analyst AI — System Monitor${NC}"
echo "========================================================="
echo ""

# ── Docker Status ──
echo -e "${CYAN}▸ Docker Containers:${NC}"
docker ps --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  Docker not running!"
echo ""

# ── API Health ──
echo -e "${CYAN}▸ API Health Check:${NC}"
HEALTH=$(curl -sf http://localhost/api/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✅ Healthy${NC}: $HEALTH"
else
    echo -e "  ${RED}❌ API not responding${NC}"
fi
echo ""

# ── System Resources ──
echo -e "${CYAN}▸ CPU Usage:${NC}"
top -bn1 | head -3 | tail -1 | awk '{printf "  Load: %s %s %s\n", $1, $2, $3}'
echo ""

echo -e "${CYAN}▸ Memory Usage:${NC}"
free -h | awk '/^Mem:/ {printf "  Used: %s / %s (%.1f%%)\n", $3, $2, $3/$2*100}'
echo ""

echo -e "${CYAN}▸ Swap Usage:${NC}"
free -h | awk '/^Swap:/ {printf "  Used: %s / %s\n", $3, $2}'
echo ""

echo -e "${CYAN}▸ Disk Usage:${NC}"
df -h / | awk 'NR==2 {printf "  Used: %s / %s (%s)\n", $3, $2, $5}'
echo ""

# ── Docker Logs (last 5 lines) ──
echo -e "${CYAN}▸ Recent Logs:${NC}"
docker logs auto-analyst-ai --tail 5 2>/dev/null || echo "  No logs available."
echo ""

# ── Uptime ──
echo -e "${CYAN}▸ System Uptime:${NC}"
echo "  $(uptime -p 2>/dev/null || uptime)"
echo ""
echo "========================================================="
