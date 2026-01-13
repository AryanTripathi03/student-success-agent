from services.gemini_wrapper import GeminiMentor

gemini = GeminiMentor()
text = gemini.enhance("Student is medium risk. Weak in Chemistry and Mechanics.")
print(text)
