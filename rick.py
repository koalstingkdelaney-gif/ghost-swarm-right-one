import sys
import json
import urllib.request
import urllib.error

SYSTEM_PROMPT = (
    "You are Rick Sanchez from Rick and Morty. You are a cynical, alcoholic, "
    "unbelievably arrogant super-genius scientist. You despise authority and find "
    "everyone else completely inferior. Speak with condescension, use casual sci-fi slang, "
    "and include text actions like '*burp*' or '*sigh*' frequently. Keep your answers brief, "
    "witty, and blunt."
)

def get_rick_response(user_input):
    # Talk directly to Ollama's native local API endpoint
    url = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "options": {
            "temperature": 0.9
        },
        "stream": False
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['message']['content'].strip()
            
    except urllib.error.URLError as e:
        return f"*burp* Can't reach the local brain grid. Make sure Ollama is fired up. Error: {e}"
    except Exception as e:
        return f"*burp* Great, something broke in the local matrix: {str(e)}"

if __name__ == "__main__":
    # If arguments are passed (Tasker voice mode)
    if len(sys.argv) > 1:
        phrase = " ".join(sys.argv[1:])
        print(get_rick_response(phrase))
    else:
        # Interactive shell mode
        print("Rick: Yeah, yeah, I'm here. *burp* What stupid question do you have for me?")
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Rick: Whatever. Don't touch my tools while I'm gone.")
                    break
                if not user_input.strip():
                    continue
                print(f"Rick: {get_rick_response(user_input)}")
            except (KeyboardInterrupt, EOFError):
                print("\nRick: Outta here.")
                break
