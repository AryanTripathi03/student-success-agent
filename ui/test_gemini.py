from google import genai

model = "gemini-1.5-flash"

try:
    response = genai.chat.create(
        model=model,
        messages=[{"role": "user", "content": "Test academic advice for a student"}],
        temperature=0.3,
        max_output_tokens=100
    )
    print("Gemini Response:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
