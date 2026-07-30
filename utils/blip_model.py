# utils/blip_model.py

import os
from PIL import Image

# Safeguard imports taaki agar transformers na ho toh app crash na kare
try:
    import torch
    from transformers import BlipProcessor, BlipForConditionalGeneration
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Global variables taaki model baar-baar load na ho aur server fast rahe
processor = None
model = None
device = None

def _initialize_blip():
    """Sirf pehli baar model load karne ke liye lazy initializer."""
    global processor, model, device
    if not HAS_TRANSFORMERS:
        raise ImportError("Error: 'torch' aur 'transformers' install nahi hain.")
    
    if model is None:
        # Check karta hai ki GPU available hai ya nahi, warna CPU use karega
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

def generate_caption_with_blip(image_path: str) -> str:
    """
    BLIP model ka use karke basic local caption generate karta hai.
    """
    if not HAS_TRANSFORMERS:
        return "Error: BLIP use karne ke liye torch aur transformers zaruri hai."

    try:
        if not os.path.exists(image_path):
            return f"Error: Image nahi mili at {image_path}."

        # Model initialize karna (agar pehle se nahi hua hai toh)
        _initialize_blip()

        # Image ko RGB mode mein open karke process karna
        with Image.open(image_path).convert('RGB') as img:
            inputs = processor(img, return_tensors="pt").to(device)
            out = model.generate(**inputs, max_new_tokens=50)
            caption = processor.decode(out[0], skip_special_tokens=True)
            return caption

    except Exception as e:
        return f"BLIP Processing Error: {str(e)}"