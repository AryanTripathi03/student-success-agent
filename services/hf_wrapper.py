import os

# Try to get the API key from environment variables or Streamlit secrets
HF_API_KEY = os.environ.get("HF_API_KEY")

if not HF_API_KEY:
    # Try using st.secrets if available
    try:
        import streamlit as st
        HF_API_KEY = st.secrets.get("HF_API_KEY")
    except Exception:
        pass

if not HF_API_KEY:
    # If still not found, give a clear error (will only be used locally)
    raise ValueError("HF_API_KEY not set. Configure it via Streamlit Secrets or local .env")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

class HFGenerator:
    def enhance(self, prompt: str, max_tokens: int = 300) -> str:
        import requests

        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": max_tokens, "temperature": 0.3},
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            raise RuntimeError(
                f"Hugging Face API request failed: {response.status_code} {response.text}"
            )

        output = response.json()

        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"].strip()
        return str(output)
