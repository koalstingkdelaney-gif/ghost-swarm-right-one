import os
import json
import time
import socket
import shutil
import logging
import subprocess
import requests

BASE_DIR = os.path.expanduser('~/GhostCorp')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'system.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_environment():
    try:
        subprocess.run("termux-wake-lock", shell=True, check=False)
    except Exception:
        pass
    
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "ollama_url": "http://127.0.0.1:11434/api/generate",
            "model": "llama3.2",
            "local_network_mode": True
        }
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=4)

class GhostCorpEngine:
    def __init__(self):
        initialize_environment()
        with open(CONFIG_PATH, 'r') as f:
            self.config = json.load(f)
        self.history = []
        self.max_history = 5

    def profile_system(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            total, used, free = shutil.disk_usage(BASE_DIR)
            storage = f"Free: {free // (2**20)} MB / Total: {total // (2**20)} MB"
            
            arp_res = subprocess.run("arp -a", shell=True, capture_output=True, text=True)
            nodes = arp_res.stdout.strip() if arp_res.stdout else "No active nodes found."
            
            return f"Host: {hostname} | IP: {local_ip}\nStorage: {storage}\nSubnet Nodes:\n{nodes}"
        except Exception as e:
            return f"Profiling error: {str(e)}"

    def execute_shell(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=20)
            output = result.stdout if result.returncode == 0 else result.stderr
            return {"code": result.returncode, "output": output.strip() if output else "No output."}
        except Exception as e:
            return {"code": -1, "output": f"Execution error: {str(e)}"}

    def detect_loop(self, action):
        recent = [h.get("action") for h in self.history[-3:]]
        return recent.count(action) >= 2

    def query_ai(self, prompt, sys_data):
        system_prompt = (
            "You are GhostCorp, an autonomous 24/7 local system utility agent. "
            "Analyze system data, maintain stability, and execute shell commands using [CMD: command]. "
            "If an error occurs or a loop is detected, adapt and try a new approach."
        )
        history_str = "\n".join([f"Action: {h['action']} | Result: {h['output']}" for h in self.history])
        full_prompt = f"{system_prompt}\n\nHistory:\n{history_str}\n\nSystem Data:\n{sys_data}\n\nDirective: {prompt}\nResponse:"

        try:
            res = requests.post(
                self.config["ollama_url"],
                json={"model": self.config["model"], "prompt": full_prompt, "stream": False},
                timeout=45
            )
            if res.status_code == 200:
                return res.json().get("response", "")
            return "Error connecting to local LLM."
        except Exception as e:
            return f"Connection exception: {str(e)}"

    def run(self):
        print("[GhostCorp] All-In-One Unified Engine Online.")
        objective = "Monitor local resources, audit network nodes, and ensure stable execution."
        
        while True:
            sys_data = self.profile_system()
            ai_text = self.query_ai(objective, sys_data)
            print(f"\n[GhostCorp Thought]:\n{ai_text}")

            if "[CMD:" in ai_text:
                start = ai_text.find("[CMD:") + 5
                end = ai_text.find("]", start)
                if end != -1:
                    cmd = ai_text[start:end].strip()
                    
                    if self.detect_loop(cmd):
                        print("[Guard] Loop detected! Forcing strategy shift...")
                        objective = f"The command '{cmd}' caused a loop. Try an alternative solution for: monitor resources and stability."
                        continue

                    print(f"[Executing]: {cmd}")
                    result = self.execute_shell(cmd)
                    print(f"[Result]: {result['output']}")

                    self.history.append({"action": cmd, "output": result["output"]})
                    if len(self.history) > self.max_history:
                        self.history.pop(0)

                    if result["code"] != 0:
                        objective = f"Command '{cmd}' failed with error: {result['output']}. Fix or adapt."
            
            time.sleep(25)

if __name__ == "__main__":
    engine = GhostCorpEngine()
    engine.run()
