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
            "core_directives": ["Multi-Server Phone Sync", "Auto-Failover Cluster"], 
            "recent_summary": "Cluster swarm initialized.", 
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
        self.providers = [
            {"name": "Groq-Llama", "url": "https://api.groq.com/openai/v1/chat/completions", "env_key": "GROQ_API_KEY"},
            {"name": "Google-Gemini-Flash", "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", "env_key": "GEMINI_API_KEY"},
            {"name": "DeepSeek-Flash", "url": "https://api.deepseek.com/v1/chat/completions", "env_key": "DEEPSEEK_API_KEY"}
        ]

    def think(self, prompt: str, context: str) -> str:
        full_prompt = f"[Cluster Context: {context}] \n\n User Directive: {prompt}"
        
        for provider in self.providers:
            api_key = os.getenv(provider["env_key"])
            if not api_key:
                continue
            
            try:
                if "gemini" in provider["name"].lower():
                    url_with_key = f"{provider['url']}?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                    res = requests.post(url_with_key, json=payload, timeout=6)
                    if res.status_code == 200:
                        return f"[{provider['name']} - Synced Node] " + res.json()["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": "llama-3.3-70b-versatile" if "groq" in provider["name"].lower() else "deepseek-chat",
                        "messages": [{"role": "user", "content": full_prompt}],
                        "max_tokens": 500
                    }
                    res = requests.post(provider["url"], json=payload, headers=headers, timeout=6)
                    if res.status_code == 200:
                        return f"[{provider['name']} - Synced Node] " + res.json()["choices"][0]["message"]["content"]
            except Exception as e:
                continue
                
        return f"[Cluster Autonomous Mode] Processed directive: '{prompt}'. (Add API key to .env for cloud inference)."

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
    <title>GhostCorpHive - Multi-Server Phone Command Center</title>
    <style>
        body { background-color: #0b0f19; color: #00ffcc; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 15px; }
        .container { max-width: 800px; margin: auto; background: #111827; border: 1px solid #00ffcc; padding: 15px; border-radius: 8px; box-shadow: 0 0 15px rgba(0,255,204,0.1); }
        h1 { text-align: center; color: #fff; text-shadow: 0 0 10px #00ffcc; font-size: 1.4em; }
        .status-box { background: #1f2937; padding: 10px; border-left: 4px solid #00ffcc; margin-bottom: 15px; font-size: 0.85em; word-break: break-all; }
        textarea { width: 100%; height: 90px; background: #0b0f19; color: #00ffcc; border: 1px solid #00ffcc; padding: 10px; border-radius: 4px; font-family: monospace; box-sizing: border-box; }
        button { background: #00ffcc; color: #0b0f19; border: none; padding: 12px; font-weight: bold; cursor: pointer; margin-top: 10px; width: 100%; border-radius: 4px; font-size: 1em; }
        button:hover { background: #00b399; }
        .output { margin-top: 15px; background: #0b0f19; border: 1px dashed #00ffcc; padding: 12px; min-height: 90px; white-space: pre-wrap; word-break: break-all; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GHOSTCORPHIVE CLUSTER</h1>
        <div class="status-box" id="statusBox">Scanning cluster nodes for phone connection...</div>
        <textarea id="promptInput" placeholder="Enter instructions..."></textarea>
        <button onclick="sendPrompt()">DISPATCH TO ACTIVE NODE</button>
        <div class="output" id="outputBox">Awaiting execution command...</div>
    </div>
    <script>
        const CLUSTER_NODES = [
            window.location.origin,
            "https://ghost-swarm-node2.onrender.com",
            "https://ghost-swarm-node3.onrender.com"
        ];

        let activeNodeUrl = window.location.origin;

        async function findActiveNode() {
            for (let node of CLUSTER_NODES) {
                try {
                    let res = await fetch(`${node}/api/health`, { method: 'GET', signal: AbortSignal.timeout(3000) });
                    if (res.ok) {
                        let data = await res.json();
                        activeNodeUrl = node;
                        document.getElementById('statusBox').innerText = `Connected Node: ${node} | Status: ONLINE | Memory: ${data.memory_summary}`;
                        return;
                    }
                } catch(e) {}
            }
            document.getElementById('statusBox').innerText = "WARNING: All cluster nodes are currently unreachable.";
        }

        findActiveNode();
        setInterval(findActiveNode, 30000);

        async function sendPrompt() {
            let prompt = document.getElementById('promptInput').value;
            if(!prompt) return;
            document.getElementById('outputBox').innerText = "Dispatching across cluster...";
            
            try {
                let res = await fetch(`${activeNodeUrl}/api/agent`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                let data = await res.json();
                document.getElementById('outputBox').innerText = data.response;
            } catch(e) {
                document.getElementById('outputBox').innerText = "Error: Active node dropped. Retrying cluster switch...";
                findActiveNode();
            }
        }
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
    
    new_summary = f"Processed: {prompt[:100]}..."
    memory.update_state(new_summary)
    
    threading.Thread(target=broadcast_state_to_peers, args=(memory.state,)).start()
    
    return jsonify({"status": "success", "response": response_text, "memory_state": memory.state["recent_summary"]})

@app.route("/api/cluster/sync", methods=["POST"])
def cluster_sync():
    data = request.get_json() or {}
    incoming_state = data.get("state")
    if incoming_state:
        memory.state = incoming_state
        memory.save()
        return jsonify({"status": "synced"})
    return jsonify({"status": "failed"}), 400

@app.route("/api/cluster/register-peer", methods=["POST"])
def register_peer():
    data = request.get_json() or {}
    peer_url = data.get("url")
    if peer_url and peer_url not in memory.state["peer_nodes"]:
        memory.state["peer_nodes"].append(peer_url)
        memory.save()
        return jsonify({"status": "peer_registered", "peers": memory.state["peer_nodes"]})
    return jsonify({"status": "invalid_or_exists"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
