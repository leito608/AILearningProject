import os, json, urllib.request
import dotenv
dotenv.load_dotenv()

KEY = os.environ["GEMINI_API_KEY"]
BASE = "https://generativelanguage.googleapis.com/v1beta"

def get(url):
    req = urllib.request.Request(url, headers={"x-goog-api-key": KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def post(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# 1) รายชื่อโมเดลที่ key นี้เรียกได้
models = get(f"{BASE}/models?pageSize=200")["models"]
print("== โมเดลสร้างข้อความ ==")
for m in models:
    if "generateContent" in m.get("supportedGenerationMethods", []):
        print(m["name"])
print("\n== โมเดล embedding ==")
for m in models:
    if "embedContent" in m.get("supportedGenerationMethods", []):
        print(m["name"])

# 2) ทดสอบ embedding
res = post(f"{BASE}/models/gemini-embedding-001:embedContent", {
    "content": {"parts": [{"text": "สวัสดี ทดสอบ"}]},
    "outputDimensionality": 768,
})
print("\nembedding ได้ความยาว:", len(res["embedding"]["values"]))