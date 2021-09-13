import json
from dataclasses import dataclass

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field
from uvicorn import Config, Server

from custom_logger import setup_logger
from redis_connection import RedisConnector

app = FastAPI()
redis_connection = RedisConnector(0)


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


@dataclass(frozen=True)
class SampleSortedSetModel:
    key: str
    value: str
    score: int


class SampleDatum(BaseModel):
    id: str = Field(None, title="id")
    value: str = Field(None, title="value")
    timestamp: int = Field(None, title="unix_time")

    def to_model(self) -> SampleSortedSetModel:
        return SampleSortedSetModel(
            key=self.id,
            value=json.dumps({"timestamp": self.timestamp, "value": self.value}),
            score=self.timestamp,
        )


@app.post("/v1/data")
def create(data: SampleDatum):
    model = data.to_model()
    redis_connection.get_redis_client().zadd(model.key, {model.value: model.score})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={})


@app.get("/v1/data/{sample_id}")
def show(sample_id: str):
    records = redis_connection.get_redis_client().zrange(
        name=sample_id, start=0, end=-1, desc=True
    )
    if not records:
        return JSONResponse(status_code=status.HTTP_200_OK, content={})
    values = [json.loads(r.decode("utf-8")) for r in records]
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"id": sample_id, "values": values}
    )


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
