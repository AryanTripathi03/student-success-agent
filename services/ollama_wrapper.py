import requests

class OllamaGenerator:
    def __init__(self, model="deepseek-r1:8b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def enhance(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.url, json=payload, timeout=300)

        if response.status_code != 200:
            raise RuntimeError(response.text)

        data = response.json()

        # 🔑 THIS IS THE IMPORTANT LINE
        return data.get("response", "").strip()
