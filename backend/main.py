import os
import json
import re
import base64
import httpx

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI PRO TRADER")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

PROMPT = """
Kamu adalah AI analis teknikal Forex profesional.
Analisis screenshot chart yang diberikan secara teliti.
Gunakan bahasa Indonesia dan gaya scalping yang selektif.

Periksa:
- Struktur harga dan momentum
- Support dan resistance
- Supply dan demand
- BOS dan CHoCH jika terlihat
- Liquidity sweep jika benar-benar terlihat
- Candlestick dan potensi entry

Jangan mengarang harga yang tidak terbaca.
Jika screenshot tidak jelas atau setup tidak valid, pilih WAIT.

Balas HANYA JSON:
{
 "signal": "BUY/SELL/WAIT",
 "pair": "nama pair",
 "entry": "harga atau area",
 "stop_loss": "harga",
 "take_profit_1": "harga",
 "take_profit_2": "harga",
 "risk_reward": "rasio",
 "quality": "0-100",
 "reason": ["alasan 1", "alasan 2"],
 "warning": "peringatan"
}
"""

@app.get("/")
def home():
    return {"status": "AI PRO TRADER API aktif"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not API_KEY:
        raise HTTPException(500, "API key belum dipasang di server.")

    if file.content_type not in [
        "image/png", "image/jpeg", "image/webp"
    ]:
        raise HTTPException(400, "Gunakan gambar PNG, JPG, atau WEBP.")

    image_data = await file.read()

    if len(image_data) > 8 * 1024 * 1024:
        raise HTTPException(400, "Ukuran gambar maksimal 8 MB.")

    encoded = base64.b64encode(image_data).decode("utf-8")

    payload = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {
                    "inline_data": {
                        "mime_type": file.content_type,
                        "data": encoded
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent?key={API_KEY}"
    )

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, json=payload)

    if response.status_code != 200:
        raise HTTPException(502, "Gagal menganalisis gambar.")

    result = response.json()
    try:
        answer = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(answer)
    except (KeyError, IndexError, ValueError):
        raise HTTPException(502, "Format analisis AI tidak valid.")
