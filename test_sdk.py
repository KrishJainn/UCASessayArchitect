
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from google import genai
    from google.genai import types
    print("SDK Import Successful")
except ImportError as e:
    print(f"SDK Import Failed: {e}")
    exit(1)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("API Key missing")
    exit(1)

print(f"API Key present: {api_key[:5]}...")

try:
    client = genai.Client(api_key=api_key)
    print("Client initialized")
    
    print(f"ThinkingConfig fields: {types.ThinkingConfig.model_fields.keys()}")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Why?",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Generation Failed: {e}")
