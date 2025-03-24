import urllib.request
import json

ollama_url = "http://ollama:11434/api/"  # Docker service URL

payload = {"model": "mymodel", "prompt": "Hello, Ollama!", "stream": False}

req = urllib.request.Request(
    ollama_url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(req, timeout=None) as response:
        result = json.loads(response.read().decode("utf-8"))
        print("Ollama response:", result["response"])
except urllib.error.URLError as e:
    print("Error contacting Ollama:", e)
