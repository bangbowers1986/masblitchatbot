# gemini_client.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Ambil API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY belum di-set di .env atau secrets!")

genai.configure(api_key=GEMINI_API_KEY)

# Inisialisasi model
model = genai.GenerativeModel('gemini-2.0-flash')  # ✅ Gratis & stabil

def ask_gemini(prompt: str, max_retries=2) -> str:
    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                    top_p=0.9,
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                ]
            )
            # ✅ Validasi respons sebelum akses .text
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                raise ValueError("Response tidak mengandung teks")
        except Exception as e:
            if attempt == max_retries:
                return f"⚠️ Maaf, Mas Blit lagi lemes. Coba tanya lagi ya? (Error: {str(e)[:50]}...)"
            continue
    return "⚠️ Error sistem. Cobain menit depan, ya?"