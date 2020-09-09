import redis


class Cache:

    link = None

    # 初始化
    @staticmethod
    def init():
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False)
        Cache.link = redis.Redis(connection_pool=pool)

    # 设置一个键值对
    @staticmethod
    def set(key, value):
        if Cache.link is None:
            Cache.init()
        Cache.link.set(key, value, ex=600)

    # 根据键取出值
    @staticmethod
    def get(key):
        if Cache.link is None:
            Cache.init()
        return Cache.link.get(key)
