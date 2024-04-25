import redis

redis_uri = 'rediss://default:AVNS_Hgnsx66qoB1HZqN97Bu@gomoku-gomoku.a.aivencloud.com:20867'
redis_client = redis.from_url(redis_uri)


class Database:
    def __getitem__(self, item: str) -> str:
        return redis_client.get(item).decode('utf-8')

    def __setitem__(self, key: str, value: str) -> None:
        redis_client.set(key, value)


database = Database()


def get_database():
    return database
