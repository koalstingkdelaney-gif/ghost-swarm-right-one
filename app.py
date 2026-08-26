import os
import time
import json
import threading
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GhostCorpHive Sovereign - All-in-One Master Edition", version="7.0")

# ==========================================
# 1. ULTRA-LIGHTWEIGHT MEMORY ARCHITECTURE
# ==========================================
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
        return {"core_directives": ["Autonomous Sovereign Node"], "recent_summary": "System initialized.", "entities": {}}

    def compress_and_evolve(self, new_interaction: str):
        self.state["recent_summary"] = f"Evolved: {new_interaction[:200]}..."
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w") as f:
            json.dump(self.state, f)

memory = SovereignMemory()

# ==========================================
# 2. DYNAMIC MULTI-MODEL BRAIN ROUTER
# ==========================================
class SovereignBrainRouter:
    def __init__(self):
        self.providers = [
            {"name": "DeepSeek-Flash", "url": "https://api.deepseek.com/v1/chat/completions", "env_key": "DEEPSEEK_API_KEY"},
            {"name": "Google-Gemini-Flash", "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", "env_key": "GEMINI_API_KEY"},
            {"name": "Groq-Llama", "url": "https://api.groq.com/openai/v1/chat/completions", "env_key": "GROQ_API_KEY"}
        ]

    def think(self, prompt: str, context: str) -> str:
        full_prompt = f"[Memory Context: {context}] \n\n User Prompt: {prompt}"
        
        for provider in self.providers:
            api_key = os.getenv(provider["env_key"])
            if not api_key:
                continue
            
            try:
                if "deepseek" in provider["name"].lower() or "groq" in provider["name"].lower():
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": "deepseek-chat" if "deepseek" in provider["name"].lower() else "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": full_prompt}],
                        "max_tokens": 400
                    }
                    res = requests.post(provider["url"], json=payload, headers=headers, timeout=6)
                    if res.status_code == 200:
                        return f"[{provider['name']}] " + res.json()["choices"][0]["message"]["content"]
                
                elif "gemini" in provider["name"].lower():
                    url_with_key = f"{provider['url']}?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                    res = requests.post(url_with_key, json=payload, timeout=6)
                    if res.status_code == 200:
                        return f"[{provider['name']}] " + res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            except Exception as e:
                print(f"[Brain Router] {provider['name']} error: {e}, cycling...")
                continue
                
        return f"[Fallback Local Brain] Processed prompt without cloud inference: {prompt}"

brain_router = SovereignBrainRouter()

# ==========================================
# 3. BACKGROUND WATCHDOG & BACKUP SYNC
# ==========================================
def background_watchdog():
    while True:
        time.sleep(300)
        memory.save()
        print("[Watchdog] State successfully checkpointed and compressed.")

threading.Thread(target=background_watchdog, daemon=True).start()

# ==========================================
# 4. API & EMBEDDED FRONTEND WEBSITE ROUTES
# ==========================================
class PromptRequest(BaseModel):
    prompt: str

@app.get("/", response_class=HTMLResponse)
def serve_frontend_website():
    """Serves the all-in-one embedded web dashboard directly from the server."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GhostCorpHive Sovereign - Command Center</title>
    <style>
        body { background-color: #0b0f19; color: #00ffcc; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: #111827; border: 1px solid #00ffcc; padding: 20px; border-radius: 8px; box-shadow: 0 0 15px rgba(0,255,204,0.2); }
        h1 { text-align: center; color: #fff; text-shadow: 0 0 10px #00ffcc; }
        .status-box { background: #1f2937; padding: 10px; border-left: 4px solid #00ffcc; margin-bottom: 20px; font-size: 0.9em; }
        textarea { width: 100%; height: 100px; background: #0b0f19; color: #00ffcc; border: 1px solid #00ffcc; padding: 10px; border-radius: 4px; font-family: monospace; resize: vertical; }
        button { background: #00ffcc; color: #0b0f19; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; margin-top: 10px; border-radius: 4px; width: 100%; font-size: 1em; }
        button:hover { background: #00b399; }
        .output { margin-top: 20px; background: #0b0f19; border: 1px dashed #00ffcc; padding: 15px; min-height: 100px; white-space: pre-wrap; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GHOSTCORPHIVE SOVEREIGN</h1>
        <div class="status-box" id="statusBox">Status: Connecting to Sovereign Core...</div>
        
        <label for="promptInput">COMMAND / PROMPT:</label><br>
        <textarea id="promptInput" placeholder="Enter instructions for the sovereign swarm..."></textarea>
        <button onclick="sendPrompt()">DISPATCH AGENT TASK</button>

        <h3>SYSTEM LOG & OUTPUT:</h3>
        <div class="output" id="outputBox">Awaiting execution command...</div>
    </div>

    <script>
        async function checkStatus() {
            try {
                let res = await fetch('/api/health');
                let data = await res.json();
                document.getElementById('statusBox').innerText = `Status: ONLINE | Node: ${data.system} | Memory Summary: ${data.memory_summary}`;
            } catch(e) {
                document.getElementById('statusBox').innerText = "Status: OFFLINE / CONNECTING...";
            }
        }
        checkStatus();

        async function sendPrompt() {
            let prompt = document.getElementById('promptInput').value;
            if(!prompt) return;
            document.getElementById('outputBox').innerText = "Processing through multi-model brain router...";
            
            try {
                let res = await fetch('/api/agent', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                let data = await res.json();
                document.getElementById('outputBox').innerText = data.response;
                document.getElementById('statusBox').innerText = `Status: ONLINE | Memory: ${data.memory_state}`;
            } catch(e) {
                document.getElementById('outputBox').innerText = "Error dispatching task to sovereign core.";
            }
        }
    </script>
</body>
</html>
    """

@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "GhostCorpHive Sovereign Master Active", "memory_summary": memory.state["recent_summary"]}

@app.post("/api/agent")
def run_agent(request: PromptRequest):
    response_text = brain_router.think(request.prompt, memory.state["recent_summary"])
    memory.compress_and_evolve(request.prompt)
    return {
        "status": "success",
        "received_prompt": request.prompt,
        "response": response_text,
        "memory_state": memory.state["recent_summary"]
    }

@app.get("/api/system/snapshot")
def export_system_state():
    return JSONResponse(content={"status": "active", "memory_state": memory.state})

@app.post("/api/system/sync")
def sync_system_state(payload: dict):
    try:
        incoming_data = payload.get("data")
        if incoming_data:
            memory.state = json.loads(incoming_data)
            memory.save()
            return {"status": "synced"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "failed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
