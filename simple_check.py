import requests
try:
    requests.get("http://127.0.0.1:11434")
    print("Ollama is RUNNING!")
except:
    print("Ollama is NOT running.")
