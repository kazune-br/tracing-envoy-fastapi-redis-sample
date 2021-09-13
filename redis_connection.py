import redis


class RedisConnector:
    def __init__(self, db_index: int):
        self._redis_connection_pool: redis.ConnectionPool = redis.ConnectionPool(
            host="redis",
            password="password",
            port=6379,
            db=db_index,
        )

    def get_redis_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self._redis_connection_pool)
