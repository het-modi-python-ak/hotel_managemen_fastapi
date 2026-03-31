import logging
import time
import json
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="a",
    force=True
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Example API")

SENSITIVE_FIELDS = {"password", "token", "access_token", "refresh_token", "authorization", "secret"}


def mask_sensitive_data(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                new_data[key] = "******"
            else:
                new_data[key] = mask_sensitive_data(value)
        return new_data

    elif isinstance(data, list):
        return [mask_sensitive_data(i) for i in data]

    return data


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.perf_counter()

        body_bytes = await request.body()
        payload = None

        if body_bytes:
            try:
                body_json = json.loads(body_bytes)
                masked_body = mask_sensitive_data(body_json)
                payload = json.dumps(masked_body)
            except Exception:
                payload = body_bytes.decode("utf-8")

        query_params = dict(request.query_params)

        logger.info(
            f"REQUEST | {request.client.host} | "
            f"{request.method} {request.url.path} | "
            f"Query: {query_params} | "
            f"Payload: {payload}"
        )

        # Restore request body so FastAPI can read it again
        async def receive():
            return {"type": "http.request", "body": body_bytes}

        request._receive = receive

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        logger.info(
            f"RESPONSE | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.4f}s"
        )

        return response


