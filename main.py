import time
import uuid
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

START_TIME = time.time()

logs = deque(maxlen=1000)

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests"
)


@app.middleware("http")
async def metrics_and_logs(request: Request, call_next):
    http_requests_total.inc()

    request_id = str(uuid.uuid4())

    logs.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
    })

    response = await call_next(request)
    return response


@app.get("/work")
def work(n: int):
    for _ in range(n):
        pass

    return {
        "email": "25f1001126@ds.study.iitm.ac.in",
        "done": n,
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME,
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(logs)[-limit:]
