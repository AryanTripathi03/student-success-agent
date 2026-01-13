# services/hf_wrapper.py
import os
import streamlit as st
import requests
from typing import Optional

# -------------------------
# Hugging Face API Key
# -------------------------
# Try to get HF_API_KEY from environment variables
HF_API_KEY: Optional[str] = os.getenv("HF_API_KEY")

# If not found, try accessing via Streamlit secrets
if not HF_API_KEY:
    HF_API_KEY = st.secrets.get("HF_API_KEY", None)

# If still not set, raise an error
if not HF_API_KEY:
    raise ValueError(
        "HF_API_KEY not set. Please configure it in .env locally or Streamlit Secrets."
    )

# -------------------------
# API Config
# -------------------------
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# -------------------------
# HF Generator Class
# -------------------------
class HFGenerator:
    """Wrapper for Hugging Face Inference API (Generative Layer)."""

    def __init__(self):
        self.api_url = API_URL
        self.headers = HEADERS

    @st.cache_data(show_spinner=False)
    def enhance(self, prompt: str, max_tokens: int = 300, temperature: float = 0.3) -> str:
        """
        Generate text from Hugging Face Mistral-7B-Instruct model.

        Args:
            prompt (str): Input prompt for the model.
            max_tokens (int): Maximum number of tokens to generate.
            temperature (float): Sampling temperature.

        Returns:
            str: Generated text.
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to reach Hugging Face API: {e}")

        if response.status_code != 200:
            raise RuntimeError(
                f"Hugging Face API request failed: {response.status_code} {response.text}"
            )

        output = response.json()

        # Safe extraction
        if isinstance(output, list) and len(output) > 0 and "generated_text" in output[0]:
            return output[0]["generated_text"].strip()

        return str(output)  # fallback
