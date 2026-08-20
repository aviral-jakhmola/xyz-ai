# test_gemini.py
from google import genai

client = genai.Client(api_key="PASTE_YOUR_AQ_KEY_HERE")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in one sentence."
)
print(response.text)