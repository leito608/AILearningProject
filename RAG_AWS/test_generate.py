import os, json, urllib.request, urllib.error
import dotenv
dotenv.load_dotenv()

KEY = os.environ["GEMINI_API_KEY"]
BASE = "https://generativelanguage.googleapis.com/v1beta/models"

CANDIDATES = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
]

payload = {
    "contents": [{"role": "user", "parts": [{"text": "ตอบสั้นๆ ว่า: เมืองหลวงของไทยคืออะไร"}]}],
    "generationConfig": {"maxOutputTokens": 200, "temperature": 0.2},
}

for model in CANDIDATES:
    req = urllib.request.Request(
        f"{BASE}/{model}:generateContent",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.loads(r.read())
        parts = res["candidates"][0]["content"].get("parts", [])
        text = parts[0]["text"].strip() if parts else "(ว่าง)"
        print(f"OK   {model}: {text[:80]}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:150].replace("\n", " ")
        print(f"FAIL {model}: HTTP {e.code} {detail}")
    except Exception as e:
        print(f"FAIL {model}: {e}")