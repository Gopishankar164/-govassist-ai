import json
import requests
from typing import Dict, Any, AsyncGenerator

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2"

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json"
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return json.loads(data.get("response", "{}"))
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return {}

    async def generate_stream(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        import aiohttp
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=60) as response:
                    async for line in response.content:
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            yield data.get("response", "")
                            if data.get("done", False):
                                break
        except Exception as e:
            yield f"Error calling Ollama: {str(e)}"

ollama_client = OllamaClient()
