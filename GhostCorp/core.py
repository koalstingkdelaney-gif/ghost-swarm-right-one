import json
import logging
import os
import requests

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'system.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"ollama_url": "http://127.0.0.1:11434/api/generate", "model": "llama3.2"}

class GhostCorpCore:
    def __init__(self):
        self.config = load_config()
        logging.info("GhostCorp Core initialized successfully.")

    def query_local_ai(self, prompt):
        payload = {
            "model": self.config.get("model", "llama3.2"),
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.config["ollama_url"], json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json().get("response", "")
                logging.info("AI query processed successfully.")
                return result
            else:
                logging.error(f"Ollama error: {response.status_code}")
                return "Error communicating with local AI model."
        except Exception as e:
            logging.error(f"Connection failed: {str(e)}")
            return "Failed to connect to local Ollama instance. Ensure it is running."

if __name__ == "__main__":
    system = GhostCorpCore()
    print("[GhostCorp] Local engine online. Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\nGhostCorp> ")
            if user_input.lower() == 'exit':
                break
            response = system.query_local_ai(user_input)
            print(f"\n[Operator]:\n{response}")
        except KeyboardInterrupt:
            break
