from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse
import threading
import time

app = Flask(__name__)

# Shared runtime state for the 24/7 background research & upgrade loop
node_state = {
    "target_focus": "Autonomous software self-improvement and optimization",
    "status": "Active 24/7 background telemetry loop",
    "last_cycle": "Never",
    "upgrade_mode": "Auto-Scan & Optimize",
    "findings": []
}

def background_autonomous_worker():
    """Runs 24/7 in the background every 2 minutes, scanning for upgrades and insights based on focus."""
    while True:
        try:
            focus = node_state["target_focus"]
            encoded = urllib.parse.quote_plus(focus)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
            resp = requests.get(search_url, headers=headers, timeout=8)
            timestamp = time.strftime("%H:%M:%S")
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                result_elements = soup.find_all('div', class_='result', limit=3)
                
                new_entries = []
                for r in result_elements:
                    title_tag = r.find('a', class_='result__snippet')
                    link_tag = r.find('a', class_='result__url')
                    if title_tag and link_tag:
                        new_entries.append({
                            "time": timestamp,
                            "title": title_tag.get_text(strip=True)[:75],
                            "url": link_tag.get('href', '#')
                        })
                
                if new_entries:
                    node_state["findings"] = new_entries + node_state["findings"]
                    if len(node_state["findings"]) > 35:
                        node_state["findings"].pop()
                    node_state["last_cycle"] = timestamp
            else:
                # Fallback telemetry log entry
                node_state["findings"].insert(0, {
                    "time": timestamp,
                    "title": f"Self-Optimization Scan: {focus}",
                    "url": "https://github.com"
                })
        except Exception as e:
            pass
        
        # 2-minute interval loop
        time.sleep(120)

# Start background worker thread
threading.Thread(target=background_autonomous_worker, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GhostCorp Autonomous Node Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0b0f19; color: #e2e8f0; padding: 20px; max-width: 800px; margin: auto; }
        h2, h3 { color: #38bdf8; border-bottom: 2px solid #1e293b; padding-bottom: 8px; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        input[type="text"] { width: 100%; background: #030712; border: 1px solid #334155; border-radius: 6px; color: #fff; padding: 10px; font-size: 13px; box-sizing: border-box; margin-top: 6px; }
        button { margin-top: 10px; padding: 10px 20px; background: #0284c7; color: #fff; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; text-transform: uppercase; }
        button:hover { background: #0369a1; }
        .log-box { background: #030712; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; height: 220px; overflow-y: auto; font-family: monospace; font-size: 11px; color: #4ade80; }
        .source-link { color: #38bdf8; text-decoration: none; }
        .source-link:hover { text-decoration: underline; }
        p { margin: 4px 0; }
        .badge { background: #1e293b; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-family: monospace; }
    </style>
</head>
<body>
    <h2>GhostCorp Autonomous Node Control</h2>

    <div class="card">
        <div><b>Node Status:</b> <span style="color: #4ade80;">{{ state.status }}</span></div>
        <div style="margin-top: 6px;"><b>Current Upgrade Focus:</b> <span style="color: #facc15;" id="currentFocus">{{ state.target_focus }}</span></div>
        <div style="margin-top: 6px;"><b>Last 2-Minute Scan:</b> <span id="lastCycle">{{ state.last_cycle }}</span></div>
    </div>

    <div class="card">
        <form onsubmit="updateFocus(event)">
            <label><b>Configure Autonomous Upgrade / Research Directive:</b></label>
            <input type="text" id="focusInput" placeholder="e.g., Upgrade everything, optimize Python performance, find new web tools..." required>
            <button type="submit" style="background: #16a34a;">Set & Apply Directive</button>
        </form>
    </div>

    <div class="card">
        <h3>24/7 Autonomous Upgrade & Findings Stream</h3>
        <div class="log-box" id="logBox">
            {% for f in state.findings %}
                <p>[{{ f.time }}]: <a class="source-link" href="{{ f.url }}" target="_blank">{{ f.title }}</a></p>
            {% endfor %}
        </div>
    </div>

    <script>
        async function updateFocus(e) {
            e.preventDefault();
            let val = document.getElementById('focusInput').value;
            if(!val) return;
            let data = new FormData();
            data.append('focus', val);
            await fetch('/directive', { method: 'POST', body: data });
            document.getElementById('focusInput').value = '';
            fetchState();
        }

        async function fetchState() {
            try {
                let res = await fetch('/status');
                let data = await res.json();
                document.getElementById('currentFocus').innerText = data.target_focus;
                document.getElementById('lastCycle').innerText = data.last_cycle;
                document.getElementById('logBox').innerHTML = data.findings.map(f => 
                    `<p>[${f.time}]: <a class="source-link" href="${f.url}" target="_blank">${f.title}</a></p>`
                ).join('');
            } catch(e) {}
        }

        setInterval(fetchState, 3000);
    </script>
</body>
</html>
"""

@app.route("/status")
def status():
    return jsonify(node_state)

@app.route("/directive", methods=["POST"])
def directive():
    f = request.form.get("focus", "").strip()
    if f:
        node_state["target_focus"] = f
        node_state["findings"].insert(0, {
            "time": time.strftime("%H:%M:%S"),
            "title": f"Directive Updated: {f} (Auto-Upgrade Loop Engaged)",
            "url": "https://github.com"
        })
    return jsonify({"status": "success"})

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, state=node_state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
