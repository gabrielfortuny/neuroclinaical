import urllib.request
import json

ollama_url = "http://ollama:11434/api/generate"  # Docker service URL

payload = {"model": "example-model", "prompt": "Hello, Ollama!", "stream": False}

req = urllib.request.Request(
    ollama_url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        print("Ollama response:", result["response"])
except urllib.error.URLError as e:
    print("Error contacting Ollama:", e)
