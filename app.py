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
            "core_directives": ["Gemini Cloud Integration", "Multi-Server Phone Sync"], 
            "recent_summary": "Gemini cluster node online.", 
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
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    def think(self, prompt: str, context: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "[Cluster Error] GEMINI_API_KEY environment variable is not configured on Render."

        full_prompt = f"System Context: {context}\n\nUser Directive: {prompt}"
        
        url_with_key = f"{self.url}?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }

        try:
            res = requests.post(url_with_key, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return f"[Google Gemini Flash - Sovereign Cloud Node]\n{content}"
            else:
                return f"[Gemini API Error Code {res.status_code}] {res.text}"
        except Exception as e:
            return f"[Cluster Connection Exception] {str(e)}"

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
    <title>GhostCorpHive - Gemini Sovereign Node</title>
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
        <h1>GHOSTCORPHIVE GEMINI NODE</h1>
        <div class="status-box" id="statusBox">Connecting to Gemini cluster node...</div>
        <textarea id="promptInput" placeholder="Enter instructions for your cluster..."></textarea>
        <button onclick="sendPrompt()">DISPATCH TO GEMINI CLUSTER</button>
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

        async function sendPrompt() {
            let prompt = document.getElementById('promptInput').value;
            if(!prompt) return;
            document.getElementById('outputBox').innerText = "Routing directly through Google Gemini cloud cluster...";
            try {
                let res = await fetch(`${activeNodeUrl}/api/agent`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                let data = await res.json();
                document.getElementById('outputBox').innerText = data.response;
            } catch(e) {
                document.getElementById('outputBox').innerText = "Error: Node communication failed.";
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
    memory.update_state(f"Processed: {prompt[:100]}...")
    threading.Thread(target=background_cluster_sync, args=(memory.state,)).start()
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
