import os
import google.generativeai as genai

class GeminiMentorshipAgent:
    """
    Uses Gemini LLM to convert AI analytics
    into high-quality academic mentorship.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def generate_insight(self, summary: str) -> str:
        """
        summary: precomputed numeric + text summary
        """

        prompt = f"""
You are an expert academic mentor.

Based on the following student analytics,
generate clear, actionable advice.

RULES:
- No greetings
- No fluff
- Focus on improving marks
- Give bullet points
- Be concise but deep

STUDENT ANALYTICS:
{summary}

OUTPUT:
"""

        response = self.model.generate_content(prompt)
        return response.text.strip()
