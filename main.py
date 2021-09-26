import json
from dataclasses import dataclass
from typing import List

from fastapi import BackgroundTasks, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from jaeger_client.codecs import B3Codec
from pydantic import BaseModel, Field
from uvicorn import Config, Server

from custom_logger import setup_logger
from redis_connection import RedisConnector
from tracer import CustomTracer

app = FastAPI()
redis_connection = RedisConnector(0)
tracer = CustomTracer()


def generate_span_ctx(request: Request):
    """
    request.headers
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
    carrier = {
        "x-request-id": request.headers.get("x-request-id"),
        "x-b3-traceid": request.headers.get("x-b3-traceid"),
        "x-b3-spanid": request.headers.get("x-b3-spanid"),
        "x-b3-sampled": request.headers.get("x-b3-sampled"),
    }
    codec = B3Codec()
    return codec.extract(carrier)


@app.get("/healthcheck")
def healthcheck():
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


class SampleData(BaseModel):
    values: List[SampleDatum] = Field(None, title="id")


@app.post("/v1/data")
def create(data: SampleDatum, span_ctx=Depends(generate_span_ctx)):
    model = data.to_model()
    with tracer.get_trace().start_active_span("redis", child_of=span_ctx) as scope:
        scope.span.set_tag("action", "insert")
        redis_connection.get_redis_client().zadd(model.key, {model.value: model.score})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={})


def insert_sample_data(datum: SampleDatum, span_ctx):
    with tracer.get_trace().start_span("redis", child_of=span_ctx) as span:
        model = datum.to_model()
        span.set_tag("action", "insert")
        span.log_kv({"key": model.key, "value": model.value, "score": model.score})
        redis_connection.get_redis_client().zadd(model.key, {model.value: model.score})


@app.post("/v1/data/bulk")
async def bulk_create(
    data: SampleData, background_tasks: BackgroundTasks, span_ctx=Depends(generate_span_ctx)
):
    with tracer.get_trace().start_active_span("access", child_of=span_ctx):
        for d in data.values:
            background_tasks.add_task(insert_sample_data, d, span_ctx)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={})


@app.get("/v1/data/{sample_id}")
def show(sample_id: str, span_ctx=Depends(generate_span_ctx)):
    # with tracer.get_trace().start_span("redis_access", child_of=span_ctx) as span:
    with tracer.get_trace().start_active_span("redis", child_of=span_ctx) as scope:
        scope.set_tag("action", "select")
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
