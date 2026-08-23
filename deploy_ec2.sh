#!/bin/bash
set -e

echo "========================================================="
echo "   🤖 Auto-Analyst AI — AWS EC2 One-Click Deploy Script   "
echo "========================================================="

# 1. Setup 2GB Swap Memory (Crucial for 1GB RAM Free Tier EC2)
if [ ! -f /swapfile ]; then
    echo "⚙️ Creating 2GB Swap Memory..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "✅ Swap memory enabled."
else
    echo "✅ Swap memory already active."
fi

# 2. System updates and Docker installation
echo "📦 Installing Docker and dependencies..."
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose git curl

# Start Docker service
sudo systemctl enable --now docker
sudo usermod -aG docker $USER || true

# 3. Environment check
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️ .env file not found. Creating from .env.example..."
        cp .env.example .env
        echo "❗ Please edit .env with your actual API keys: nano .env"
    else
        echo "❌ .env file missing! Please create .env with GROQ_API_KEY and E2B_API_KEY."
        exit 1
    fi
fi

# 4. Create data directories
mkdir -p data/input data/output

# 5. Build and launch Docker containers
echo "🚀 Building and starting Auto-Analyst AI containers..."
sudo docker-compose down || true
sudo docker-compose up -d --build

# 6. Fetch Public IP
PUBLIC_IP=$(curl -s https://checkip.amazonaws.com || curl -s ifconfig.me || echo "<YOUR-EC2-PUBLIC-IP>")

echo ""
echo "========================================================="
echo "   🎉 AUTO-ANALYST AI IS NOW LIVE ON AWS EC2!           "
echo "========================================================="
echo "   🌐 Streamlit Web UI:   http://${PUBLIC_IP}:8501"
echo "   🔌 FastAPI Backend:    http://${PUBLIC_IP}:8000"
echo "   📄 API Docs (Swagger): http://${PUBLIC_IP}:8000/docs"
echo "========================================================="
echo "To view logs: sudo docker-compose logs -f"
echo "To stop app:  sudo docker-compose down"
echo "========================================================="
