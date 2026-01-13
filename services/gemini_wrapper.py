# services/gemini_wrapper.py
from google import genai

class GeminiMentor:
    """
    Minimal, free-tier safe Gemini wrapper.
    Generates concise, actionable academic mentorship using service account auth.
    """

    def __init__(self):
        self.model = "gemini-1.5-flash"

    def enhance(self, structured_insight: str) -> str:
        """
        Enhance local mentorship insights using Gemini.
        """
        prompt = f"""
You are a top-tier academic mentor.

Improve clarity and usefulness of this academic insight.
Do NOT invent marks or change the meaning.
Be concise, professional, and actionable.

Insight:
{structured_insight}
"""
        try:
            response = genai.chat.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_output_tokens=300
            )
            return response.choices[0].message.content.strip()

        except Exception:
            return (
                f"Gemini mentor unavailable (API or quota issue).\n\n"
                f"Using local insights instead.\n\n{structured_insight}"
            )
