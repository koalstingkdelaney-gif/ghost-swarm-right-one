import os
import time
import json
import threading
import requests
from flask import Flask, jsonify, request, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

class SovereignMemory:
    def __init__(self, memory_file="GhostCorp/memory_core.json"):
        self.memory_file = memory_file
        self.load()

    def load(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    self.state = json.load(f)
            except:
                self.state = self.default_state()
        else:
            self.state = self.default_state()
            self.save()

    def default_state(self):
        return {
            "core_directives": ["Gemini 3.7 Flash Cloud Engine", "Cyberpunk Terminal UI", "Autonomous Swarm Sync"], 
            "recent_summary": "Sovereign node online. Systems operational.", 
            "peer_nodes": []
        }

    def update_state(self, new_summary: str, peers: list = None):
        self.state["recent_summary"] = new_summary
        if peers:
            self.state["peer_nodes"] = peers
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w") as f:
            json.dump(self.state, f)

memory = SovereignMemory()

class SovereignBrainRouter:
    def __init__(self):
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent"

    def think(self, prompt: str, context: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "[CRITICAL ERROR] GEMINI_API_KEY environment variable missing from runtime container."

        full_prompt = f"System Context: {context}\n\nUser Directive: {prompt}\n\n(Style Guide: Respond with elite, futuristic, hacker-style operational flair matching the GhostCorp aesthetic.)"
        
        url_with_key = f"{self.url}?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }

        try:
            res = requests.post(url_with_key, json=payload, timeout=50)
            if res.status_code == 200:
                data = res.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return f"[GHOSTCORP KERNEL // GEMINI-3.7-FLASH ACTIVE]\n{content}"
            else:
                return f"[NEURAL LINK ERROR {res.status_code}] {res.text}"
        except Exception as e:
            return f"[CLUSTER EXCEPTION] {str(e)}"

brain_router = SovereignBrainRouter()

def broadcast_state_to_peers(state_data):
    for peer_url in memory.state.get("peer_nodes", []):
        try:
            requests.post(f"{peer_url}/api/cluster/sync", json={"state": state_data}, timeout=5)
        except:
            pass

def background_cluster_sync():
    while True:
        time.sleep(180)
        broadcast_state_to_peers(memory.state)

threading.Thread(target=background_cluster_sync, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GHOSTCORP // NEURAL COMMAND</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

        body {
            background-color: #030508;
            color: #00ff66;
            font-family: 'Share Tech Mono', monospace;
            margin: 0;
            padding: 10px;
            overflow-x: hidden;
        }

        body::before {
            content: " ";
            display: block;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            z-index: 99999;
            background-size: 100% 2px, 3px 100%;
            pointer-events: none;
        }

        .container {
            max-width: 850px;
            margin: auto;
            background: rgba(5, 10, 18, 0.95);
            border: 1px solid #00ff66;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 0 25px rgba(0, 255, 102, 0.2);
        }

        h1 {
            text-align: center;
            color: #fff;
            text-shadow: 0 0 12px #00ff66;
            font-size: 1.8em;
            margin-top: 0;
            letter-spacing: 2px;
        }

        .status-box {
            background: #08111d;
            border-left: 4px solid #00ff66;
            padding: 12px;
            margin-bottom: 15px;
            font-size: 0.9em;
            word-break: break-all;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }

        .terminal-prompt-label {
            color: #00b347;
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }

        textarea {
            width: 100%;
            height: 100px;
            background: #020408;
            color: #00ff66;
            border: 1px solid #00ff66;
            padding: 12px;
            border-radius: 4px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1.1em;
            box-sizing: border-box;
            resize: vertical;
            outline: none;
            box-shadow: inset 0 0 8px rgba(0,255,102,0.1);
        }

        textarea:focus {
            border-color: #fff;
            box-shadow: 0 0 10px rgba(0,255,102,0.4);
        }

        button {
            background: #00ff66;
            color: #030508;
            border: none;
            padding: 14px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 12px;
            width: 100%;
            border-radius: 4px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1.2em;
            letter-spacing: 1px;
            transition: all 0.2s ease;
            box-shadow: 0 0 15px rgba(0,255,102,0.3);
        }

        button:hover {
            background: #fff;
            color: #030508;
            box-shadow: 0 0 20px #fff;
        }

        button:disabled {
            background: #0e2617;
            color: #005522;
            cursor: not-allowed;
            box-shadow: none;
        }

        .output-container {
            margin-top: 20px;
            background: #020408;
            border: 1px dashed #00ff66;
            padding: 15px;
            border-radius: 4px;
            min-height: 140px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 1em;
            line-height: 1.4;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
        }

        .matrix-glow {
            animation: pulseGlow 2s infinite alternate;
        }

        @keyframes pulseGlow {
            from { text-shadow: 0 0 5px #00ff66; }
            to { text-shadow: 0 0 15px #00ff66, 0 0 25px #00ff66; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="matrix-glow">⚡ GHOSTCORP SWARM HIVE ⚡</h1>
        <div class="status-box" id="statusBox">INITIALIZING NEURAL LINK TO RENDER HOST...</div>
        
        <span class="terminal-prompt-label">> ENTER DIRECTIVE FOR CLOUD SWARM:</span>
        <textarea id="promptInput" placeholder="Type instructions, upgrades, or bot scripts here..."></textarea>
        
        <button id="dispatchBtn" type="button">EXECUTE NEURAL DISPATCH</button>
        
        <span class="terminal-prompt-label" style="margin-top: 20px;">> KERNEL OUTPUT STREAM:</span>
        <div class="output-container" id="outputBox">Awaiting operator instruction...</div>
    </div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const activeNodeUrl = window.location.origin;

            async function fetchSystemHealth() {
                try {
                    let res = await fetch(`${activeNodeUrl}/api/health`, { method: 'GET', signal: AbortSignal.timeout(4000) });
                    if (res.ok) {
                        let data = await res.json();
                        document.getElementById('statusBox').innerText = `NODE: ${activeNodeUrl} | STATUS: ONLINE [SECURE] | MEMORY: ${data.memory_summary}`;
                    }
                } catch(e) {
                    document.getElementById('statusBox').innerText = `NODE: ${activeNodeUrl} | STATUS: WARNING (Telemetry link offline)`;
                }
            }
            fetchSystemHealth();

            async function sendPrompt() {
                let promptField = document.getElementById('promptInput');
                let btn = document.getElementById('dispatchBtn');
                let output = document.getElementById('outputBox');
                
                if(!promptField || !promptField.value.trim()) return;
                let promptText = promptField.value;

                btn.disabled = true;
                btn.innerText = "SYNTHESIZING VIA GEMINI 3.7...";
                output.innerText = "[*] Routing packet to Gemini cloud cluster...\n[*] Establishing secure socket connection...\n[*] Awaiting execution return...";

                try {
                    let controller = new AbortController();
                    let timeoutId = setTimeout(() => controller.abort(), 60000);

                    let res = await fetch(`${activeNodeUrl}/api/agent`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({prompt: promptText}),
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    let data = await res.json();
                    
                    output.innerText = "";
                    let text = data.response;
                    let i = 0;
                    function typeWriter() {
                        if (i < text.length) {
                            output.innerText += text.charAt(i);
                            i++;
                            setTimeout(typeWriter, 5);
                            output.scrollTop = output.scrollHeight;
                        }
                    }
                    typeWriter();

                } catch(e) {
                    output.innerText = "[ERROR] Transmission interrupted. Request timed out or node failed to respond.";
                } finally {
                    btn.disabled = false;
                    btn.innerText = "EXECUTE NEURAL DISPATCH";
                }
            }

            const btn = document.getElementById('dispatchBtn');
            if(btn) {
                btn.addEventListener('click', sendPrompt);
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/health")
def health():
    return jsonify({"status": "online", "memory_summary": memory.state["recent_summary"], "peers": memory.state.get("peer_nodes", [])})

@app.route("/api/agent", methods=["POST"])
def agent():
    data = request.get_json() or {}
    prompt = data.get("prompt", "")
    response_text = brain_router.think(prompt, memory.state["recent_summary"])
    memory.update_state(f"Processed: {prompt[:100]}...")
    return jsonify({"status": "success", "response": response_text, "memory_state": memory.state["recent_summary"]})

@app.route("/api/cluster/sync", methods=["POST"])
def cluster_sync():
    data = request.get_json() or {}
    if data.get("state"):
        memory.state = data.get("state")
        memory.save()
        return jsonify({"status": "synced"})
    return jsonify({"status": "failed"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
