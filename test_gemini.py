import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="models/gemini-flash-latest",
    contents="ഒരു കുട്ടിക്ക് പനി ഉണ്ടെങ്കിൽ എന്ത് ചെയ്യണം?"
)

print("----- Gemini Response -----")
print(response.text)
