import requests
import sys

def check_ollama():
    print("--- OLLAMA DIAGNOSTIC TOOL ---")
    url = "http://127.0.0.1:11434"
    
    # 1. Check if Server is UP
    try:
        print(f"1. Ping {url}...")
        requests.get(url, timeout=2)
        print("   ✅ Server is UP and reachable.")
    except Exception as e:
        print(f"   ❌ FAILED to connect: {e}")
        print("\n   [ACTION REQUIRED] Please open the 'Ollama' application from your Start Menu.")
        return

    # 2. Check for Models
    try:
        print("2. Checking available models...")
        resp = requests.get(f"{url}/api/tags", timeout=2)
        models = [m['name'] for m in resp.json()['models']]
        print(f"   Found models: {models}")
        
        target_model = "llama3.2:3b"
        if target_model not in models and f"{target_model}:latest" not in models:
            print(f"   ❌ Model '{target_model}' not found!")
            print(f"   [ACTION REQUIRED] Run: ollama pull {target_model}")
        else:
            print(f"   ✅ Model '{target_model}' is available.")
            
    except Exception as e:
        print(f"   ❌ Failed to list models: {e}")

    # 3. Test Generation
    try:
        print("3. Testing simple generation...")
        payload = {
            "model": "llama3.2:3b",
            "prompt": "Say 'OK' if you can hear me.",
            "stream": False
        }
        resp = requests.post(f"{url}/api/generate", json=payload, timeout=10)
        print(f"   Response status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   Output: {resp.json().get('response', '').strip()}")
            print("   ✅ Ollama is fully functional!")
        else:
            print(f"   ❌ Generation failed: {resp.text}")
    except Exception as e:
        print(f"   ❌ Generation error: {e}")

if __name__ == "__main__":
    check_ollama()
