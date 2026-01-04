import requests

def ollama_generate(host: str, model: str, prompt: str) -> str:
    """
    Generate a completion from Ollama.
    """
    url = f"{host}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        return f"[Alfred Error] LLM call failed: {e}"

def list_models(host: str) -> list[str]:
    """
    List available Ollama models.
    """
    try:
        resp = requests.get(f"{host}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

def check_connection(host: str) -> bool:
    try:
        requests.get(f"{host}/api/tags", timeout=2)
        return True
    except Exception:
        return False
