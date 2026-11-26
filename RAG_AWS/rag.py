import os, sys, json, time, math, glob, hashlib
import urllib.request, urllib.error
import dotenv
dotenv.load_dotenv()

KEY = os.environ["GEMINI_API_KEY"]
BASE = "https://generativelanguage.googleapis.com/v1beta/models"
EMB_MODEL = "gemini-embedding-001"
GEN_MODEL = "gemini-3.5-flash-lite"
INDEX_FILE = "index.json"
CHUNK, OVERLAP = 800, 100


def call(model, method, payload, retries=6):
    for i in range(retries):
        req = urllib.request.Request(
            f"{BASE}/{model}:{method}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < retries - 1:
                wait = 10 * (i + 1)
                print(f"  (HTTP {e.code} รอ {wait}s แล้วลองใหม่)")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:300]}")


def normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def embed(text, task):
    res = call(EMB_MODEL, "embedContent", {
        "content": {"parts": [{"text": text}]},
        "taskType": task,
        "outputDimensionality": 768,
    })
    return normalize(res["embedding"]["values"])


def chunks(text):
    i = 0
    while i < len(text):
        yield text[i:i + CHUNK]
        i += CHUNK - OVERLAP


def build_index():
    old = {}
    if os.path.exists(INDEX_FILE):
        for d in json.load(open(INDEX_FILE, encoding="utf-8")):
            old[d["id"]] = d          # ใช้ซ้ำ ไม่เสียโควตา embed ใหม่

    index, new_calls = [], 0
    files = sorted(glob.glob("docs/*.txt") + glob.glob("docs/*.md"))
    if not files:
        sys.exit("ไม่พบไฟล์ใน docs/")
    for path in files:
        text = open(path, encoding="utf-8").read()
        for c in chunks(text):
            cid = hashlib.sha1(c.encode()).hexdigest()
            if cid in old:
                index.append(old[cid])
                continue
            index.append({"id": cid, "source": os.path.basename(path),
                          "text": c, "emb": embed(c, "RETRIEVAL_DOCUMENT")})
            new_calls += 1
            print(f"embed แล้ว {new_calls} chunk", end="\r")
            time.sleep(1.5)           # เลี่ยงชนขีดจำกัดต่อนาที
    json.dump(index, open(INDEX_FILE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"\nเสร็จ: {len(index)} chunks (เรียก embed ใหม่ {new_calls} ครั้ง)")


def ask(q, index):
    qv = embed(q, "RETRIEVAL_QUERY")
    top = sorted(index, key=lambda d: sum(a * b for a, b in zip(qv, d["emb"])),
                 reverse=True)[:4]
    ctx = "\n\n".join(d["text"] for d in top)
    res = call(GEN_MODEL, "generateContent", {
        "systemInstruction": {"parts": [{"text":
            "ตอบจากบริบทที่ให้เท่านั้น ถ้าบริบทไม่มีข้อมูลให้บอกว่าไม่ทราบ "
            "ตอบเป็นภาษาเดียวกับคำถาม"}]},
        "contents": [{"role": "user",
                      "parts": [{"text": f"บริบท:\n{ctx}\n\nคำถาม: {q}"}]}],
        "generationConfig": {"maxOutputTokens": 800, "temperature": 0.2},
    })
    parts = res["candidates"][0]["content"].get("parts", [])
    answer = parts[0]["text"].strip() if parts else "(ไม่ได้รับคำตอบ)"
    return answer, sorted({d["source"] for d in top})


def chat():
    index = json.load(open(INDEX_FILE, encoding="utf-8"))
    print(f"โหลด {len(index)} chunks พร้อมแล้ว (พิมพ์ q เพื่อออก)")
    while True:
        q = input("\nคำถาม> ").strip()
        if q.lower() in ("q", "quit", "exit"):
            break
        if q:
            a, src = ask(q, index)
            print(f"\n{a}\n\n[แหล่งที่มา: {', '.join(src)}]")


if __name__ == "__main__":
    {"index": build_index, "chat": chat}[sys.argv[1]]()