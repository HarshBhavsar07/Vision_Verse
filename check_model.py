import os
from google import genai
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Debug: API Key found? {'YES' if api_key else 'NO'}")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Debug: Client initialized, fetching models...")
        models = list(client.models.list())
        
        if not models:
            print("Debug: No models found for this API key.")
        else:
            print(f"Success! Found {len(models)} models:")
            for model in models:
                print(f"Name: {model.name}")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
else:
    print("ERROR: GEMINI_API_KEY missing in .env file!")