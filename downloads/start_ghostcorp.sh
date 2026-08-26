#!/data/data/com.termux/files/usr/bin/bash
# GhostCorpHive — Clean single-instance launcher

echo "🔧 Cleaning up old processes..."
pkill -f "ollama serve" 2>/dev/null
pkill -f "http.server" 2>/dev/null
sleep 2

echo "🧠 Starting Ollama..."
OLLAMA_ORIGINS="*" ollama serve &
sleep 3

echo "🌐 Starting web server..."
cd ~/downloads 2>/dev/null || cd ~
python -m http.server 8181 &
sleep 1

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   👻 GhostCorpHive ALIVE                     ║"
echo "║   Open Chrome: http://127.0.0.1:8181/        ║"
echo "║   ghostcorphive_v5.html                      ║"
echo "║   Press Ctrl+C to stop                       ║"
echo "╚══════════════════════════════════════════════╝"

# Keep terminal alive
wait
