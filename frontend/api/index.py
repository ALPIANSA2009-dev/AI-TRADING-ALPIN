import os
import base64
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

@app.get("/")
def home():
    return {"status": "AI PRO TRADER aktif"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not key:
        raise HTTPException(500, "API key belum dipasang")

    if file.content_type not in ["image/png", "image/jpeg", "image/webp"]:
        raise HTTPException(400, "Format gambar tidak didukung")

    data = await file.read()

    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(400, "Maksimal 8 MB")

    prompt = """
    Analisis screenshot chart Forex secara selektif.
    Periksa struktur harga, momentum, support resistance,
    supply demand dan candle confirmation.

    Jangan mengarang harga.
    Jika setup tidak jelas, pilih WAIT.

    Balas JSON:
    {
      "signal":"BUY/SELL/WAIT",
      "pair":"pair",
      "entry":"harga",
      "stop_loss":"harga",
      "take_profit_1":"harga",
      "take_profit_2":"harga",
      "risk_reward":"rasio",
      "quality":"0-100",
      "reason":["alasan"],
      "warning":"peringatan"
    }
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {
                    "mime_type": file.content_type,
                    "data": base64.b64encode(data).decode()
                }}
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent?key={key}"
    )

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload)

    if response.status_code != 200:
        raise HTTPException(502, "Gemini gagal menganalisis")

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise HTTPException(502, "Hasil AI tidak valid")
