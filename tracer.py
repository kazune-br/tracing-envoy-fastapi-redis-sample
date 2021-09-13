from jaeger_client import Config, Tracer


class CustomTracer:
    def __init__(self):
        config = Config(
            config={
                "sampler": {
                    "type": "const",
                    "param": 1,
                },
                "local_agent": {
                    "reporting_host": "jaeger",
                    "reporting_port": "6831",
                },
                "propagation": "b3",
                "logging": True,
            },
            service_name="app",
        )
        self._tracer = config.initialize_tracer()

    def get_trace(self) -> Tracer:
        return self._tracer
