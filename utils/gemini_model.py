import os
import json
import io
from PIL import Image
from pydantic import BaseModel
from google import genai 
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Client setup
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class VisionVerseAnalysis(BaseModel):
    caption: str
    description: str
    mood: str
    scene: str
    objects: str
    instagram: str
    hashtags: str
    creative: str
    alt_text: str

def analyze_image_with_gemini(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = (
            "Analyze this image comprehensively. Generate a catchy caption, an extremely "
            "detailed description, define the overall emotional mood, break down the scene type, "
            "list key objects detected, create a ready-to-use Instagram caption with companion "
            "hashtags, provide a creative/philosophical thought inspired by the visual, and "
            "write a standard accessible alt text descriptor. Ensure all keys are filled."
        )

        # Yahan correct model name use kar rahe hain
        response = client.models.generate_content(
            model='models/gemini-3.5-flash', 
            contents=[img, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VisionVerseAnalysis,
                temperature=0.7,
            ),
        )

        return json.loads(response.text)

    except Exception as e:
        return {"error": f"API Error: {str(e)}"}