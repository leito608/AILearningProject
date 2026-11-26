import json, os, math, time, hmac, hashlib, urllib.request, urllib.error
import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
APP_PASSWORD = os.environ["APP_PASSWORD"]
GEN_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
EMB_MODEL = "gemini-embedding-001"
BASE = "https://generativelanguage.googleapis.com/v1beta/models"
PREFIX = "docs/"
MAX_BATCH = 10          # chunk ต่อ 1 request
MAX_CHUNK_CHARS = 2000
_cache = {}             # key -> (etag, data)

SESSION_SECONDS = 8 * 3600
COOKIE = "rag_session"

LOGIN_HTML = """<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>เข้าสู่ระบบ</title>
<style>
:root{--bg:#f6f5f1;--panel:#fff;--fg:#1d2321;--mute:#68716d;--line:#d9d8d0;--accent:#1f5c4d;--accent-fg:#fff;--err:#a3341f}
@media(prefers-color-scheme:dark){:root{--bg:#141917;--panel:#1b211f;--fg:#e6ebe8;--mute:#8d9792;--line:#313a36;--accent:#58b79e;--accent-fg:#0f1513;--err:#ff9b86}}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--fg);font-family:system-ui,sans-serif}
form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1.4rem;width:min(92vw,360px)}
h1{font-size:1.2rem;margin:0 0 1rem}
input,button{font:inherit;width:100%;padding:.65rem .8rem;border-radius:8px}
input{border:1px solid var(--line);background:var(--bg);color:var(--fg)}
button{margin-top:.8rem;border:1px solid var(--accent);background:var(--accent);color:var(--accent-fg);cursor:pointer}
button:disabled{opacity:.5}
input:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
#err{color:var(--err);font-size:.9rem;min-height:1.4rem;margin:.6rem 0 0}
</style></head><body>
<form id="f"><h1>เข้าสู่ระบบ</h1>
<input id="p" type="password" placeholder="รหัสผ่าน" autocomplete="current-password" autofocus required>
<button id="b">เข้าใช้งาน</button><p id="err"></p></form>
<script>
document.getElementById("f").onsubmit=async e=>{
  e.preventDefault();
  const b=document.getElementById("b"),err=document.getElementById("err");
  b.disabled=true;err.textContent="";
  try{
    const r=await fetch(location.pathname,{method:"POST",headers:{"content-type":"application/json"},
      body:JSON.stringify({action:"login",password:document.getElementById("p").value})});
    if(r.ok){location.reload();return;}
    const j=await r.json().catch(()=>({}));
    err.textContent=j.error||"เข้าสู่ระบบไม่สำเร็จ";
  }catch(x){err.textContent="เชื่อมต่อไม่ได้ ลองใหม่อีกครั้ง";}
  b.disabled=false;
};
</script></body></html>"""


def sign(exp):
    return hmac.new(APP_PASSWORD.encode(), str(exp).encode(), hashlib.sha256).hexdigest()


def make_cookie():
    exp = int(time.time()) + SESSION_SECONDS
    return (f"{COOKIE}={exp}.{sign(exp)}; Max-Age={SESSION_SECONDS}; Path=/; "
            "HttpOnly; Secure; SameSite=Strict")


def is_authed(event):
    for c in event.get("cookies") or []:
        if c.startswith(COOKIE + "="):
            try:
                exp, sig = c.split("=", 1)[1].split(".", 1)
                return int(exp) > time.time() and hmac.compare_digest(sig, sign(exp))
            except ValueError:
                return False
    return False


def reply(code, obj):
    return {"statusCode": code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(obj, ensure_ascii=False)}


def gemini(model, method, payload, retries=3):
    for i in range(retries):
        req = urllib.request.Request(
            f"{BASE}/{model}:{method}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY},
        )
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < retries - 1:
                time.sleep(6 * (i + 1))
                continue
            raise


def normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def embed_batch(texts, task):
    res = gemini(EMB_MODEL, "batchEmbedContents", {"requests": [{
        "model": f"models/{EMB_MODEL}",
        "content": {"parts": [{"text": t}]},
        "taskType": task,
        "outputDimensionality": 768,
    } for t in texts]})
    return [normalize(e["values"]) for e in res["embeddings"]]


def doc_id(name):
    return hashlib.sha1(name.encode("utf-8")).hexdigest()[:12]


def load_all():
    docs, token = {}, None
    while True:
        kw = {"Bucket": BUCKET, "Prefix": PREFIX}
        if token:
            kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            k, etag = o["Key"], o["ETag"]
            # ข้าม "โฟลเดอร์" ว่างที่สร้างจากหน้า S3 และไฟล์ที่ไม่ใช่ .json
            if k.count("/") != 2 or not k.endswith(".json") or o["Size"] == 0:
                continue
            if k not in _cache or _cache[k][0] != etag:
                body = s3.get_object(Bucket=BUCKET, Key=k)["Body"].read()
                _cache[k] = (etag, json.loads(body))
            d = _cache[k][1]
            e = docs.setdefault(k.split("/")[1], {"name": d["name"], "chunks": []})
            e["chunks"].extend(d["chunks"])
        if not r.get("IsTruncated"):
            return docs
        token = r["NextContinuationToken"]


def do_ingest(b):
    name = str(b.get("name", ""))[:200]
    part = int(b.get("part", 0))
    chunks = [str(c)[:MAX_CHUNK_CHARS] for c in (b.get("chunks") or [])][:MAX_BATCH]
    if not name or not chunks:
        return reply(400, {"error": "ข้อมูลไม่ครบ"})
    vecs = embed_batch(chunks, "RETRIEVAL_DOCUMENT")
    data = {"name": name, "chunks": [{"text": t, "emb": v} for t, v in zip(chunks, vecs)]}
    s3.put_object(Bucket=BUCKET, Key=f"{PREFIX}{doc_id(name)}/{part:05d}.json",
                  Body=json.dumps(data, ensure_ascii=False).encode("utf-8"))
    return reply(200, {"ok": True, "chunks": len(chunks)})


def do_delete(b):
    prefix = f"{PREFIX}{doc_id(str(b.get('name', '')))}/"
    r = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    keys = [{"Key": o["Key"]} for o in r.get("Contents", [])]
    if keys:
        s3.delete_objects(Bucket=BUCKET, Delete={"Objects": keys})
    return reply(200, {"ok": True})


def do_list():
    docs = load_all()
    return reply(200, {"docs": sorted(
        [{"name": d["name"], "chunks": len(d["chunks"])} for d in docs.values()],
        key=lambda x: x["name"])})


def do_ask(b):
    q = str(b.get("question", "")).strip()[:500]
    if not q:
        return reply(400, {"error": "ไม่มีคำถาม"})
    pool = [(d["name"], c) for d in load_all().values() for c in d["chunks"]]
    if not pool:
        return reply(200, {"answer": "ยังไม่มีเอกสาร กรุณาอัปโหลดเอกสารก่อน", "sources": []})
    qv = embed_batch([q], "RETRIEVAL_QUERY")[0]
    top = sorted(pool, key=lambda p: sum(a * b for a, b in zip(qv, p[1]["emb"])),
                 reverse=True)[:5]
    ctx = "\n\n".join(f"[{n}]\n{c['text']}" for n, c in top)
    res = gemini(GEN_MODEL, "generateContent", {
        "systemInstruction": {"parts": [{"text":
            "ตอบจากบริบทที่ให้เท่านั้น ถ้าบริบทไม่มีข้อมูลให้บอกว่าไม่พบในเอกสาร "
            "ตอบเป็นภาษาเดียวกับคำถาม"}]},
        "contents": [{"role": "user", "parts": [{"text": f"บริบท:\n{ctx}\n\nคำถาม: {q}"}]}],
        "generationConfig": {"maxOutputTokens": 900, "temperature": 0.2},
    })
    parts = res["candidates"][0]["content"].get("parts", [])
    answer = parts[0]["text"].strip() if parts else "ไม่ได้รับคำตอบ ลองถามใหม่"
    return reply(200, {"answer": answer, "sources": sorted({n for n, _ in top})})


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
    if method == "GET":
        if not is_authed(event):
            return {"statusCode": 200,
                    "headers": {"Content-Type": "text/html; charset=utf-8",
                                "Cache-Control": "no-store"},
                    "body": LOGIN_HTML}
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
        with open(path, encoding="utf-8") as f:
            return {"statusCode": 200,
                    "headers": {"Content-Type": "text/html; charset=utf-8",
                                "Cache-Control": "no-store"},
                    "body": f.read()}

    try:
        b = json.loads(event.get("body") or "{}")
    except Exception:
        return reply(400, {"error": "ข้อมูลไม่ถูกต้อง"})
    action = b.get("action")

    if action == "login":
        ok = hmac.compare_digest(str(b.get("password", "")).encode(), APP_PASSWORD.encode())
        if not ok:
            time.sleep(1)  # หน่วงเวลาลดการเดารหัส
            return reply(401, {"error": "รหัสผ่านไม่ถูกต้อง"})
        resp = reply(200, {"ok": True})
        resp["cookies"] = [make_cookie()]
        return resp

    if not is_authed(event):
        return reply(401, {"error": "กรุณาเข้าสู่ระบบ"})

    try:
        if action == "ingest":
            return do_ingest(b)
        if action == "delete":
            return do_delete(b)
        if action == "list":
            return do_list()
        if action == "ask":
            return do_ask(b)
        return reply(400, {"error": "คำสั่งไม่ถูกต้อง"})
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return reply(429, {"error": "โควตาฟรีของ Gemini เต็มชั่วคราว รอสักครู่แล้วลองใหม่"})
        return reply(502, {"error": f"เรียก Gemini ไม่สำเร็จ (HTTP {e.code})"})
    except Exception as e:
        print("ERROR", repr(e))
        return reply(500, {"error": f"เกิดข้อผิดพลาดภายในระบบ: {type(e).__name__}: {str(e)[:250]}"})
