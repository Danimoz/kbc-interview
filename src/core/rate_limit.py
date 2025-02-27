import redis
from src.core.config import settings


class RateLimiter:
  def __init__(self):
    self.redis_client = redis.from_url(settings.REDIS_URL)
    self.limit = 1
    self.ttl = 86400

  async def check_limit(self, user_id: str) -> bool:
    '''
    Check if user has exceeded their rate limit
    '''
    key = f"rate_limit:{user_id}"
    current_count = self.redis_client.get(key)
    current_count = int(current_count) if current_count else 0
    if current_count >= self.limit:
      return False
    return True
  
  async def increment_count(self, user_id: str) -> None:
    '''
    Increment the rate limit count
    '''
    key = f"rate_limit:{user_id}"
    current_count = self.redis_client.get(key)
    current_count = int(current_count) if current_count else 0
    self.redis_client.set(key, current_count + 1, ex=self.ttl)
  
# Create a singleton instance
rate_limiter = RateLimiter()