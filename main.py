from fastapi import FastAPI, Request
from loguru import logger
from uvicorn import Config, Server

from custom_logger import setup_logger

app = FastAPI()


@app.get("/healthcheck")
def healthcheck(request: Request):
    """
    Headers({
        'host': 'localhost:9000',
        'user-agent': 'curl/7.64.1',
        'accept': '*/*',
        'x-forwarded-proto': 'http',
        'x-request-id': 'b0c2ff03-8ef3-9401-98a1-2547cbc1e78b',
        'x-envoy-expected-rq-timeout-ms': '15000',
        'x-b3-traceid': '2041ad32cab8dc02',
        'x-b3-spanid': '2041ad32cab8dc02',
        'x-b3-sampled': '1'
    })
    """
    logger.info(request.headers)
    return {"healthcheck": "ok"}


if __name__ == "__main__":
    server = Server(
        Config(
            app=app,
            host="0.0.0.0",
            port=8000,
        ),
    )
    setup_logger()
    server.run()
