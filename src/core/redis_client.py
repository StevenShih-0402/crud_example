import redis
from django.conf import settings

# 全專案共用同一個 Redis client。
# redis-py 內部自帶連線池，且建立 client 時不會立刻連線（第一次下指令才連），
# 所以在模組層級建立即可，import 時不會因為 Redis 沒開而報錯。
# decode_responses=True：讀回來的值自動轉成 str，不必自己 .decode()
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
