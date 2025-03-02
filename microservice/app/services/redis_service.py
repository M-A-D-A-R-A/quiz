import redis
from typing import Optional, Dict

class RedisApi:
    def __init__(self, host: str = None, port: int = 6379, password: Optional[str] = None, **kwargs):
        """
        Initialize the Redis client with optional parameters.
        
        :param host: Redis server hostname or IP
        :param port: Redis server port (default: 6379)
        :param password: Optional authentication password
        :param kwargs: Additional Redis settings like `db`, `socket_timeout`, etc.
        """
        self.host = host
        self.port = port
        self.password = password
        self.client: Optional[redis.Redis] = None
        
        if host:
            self.init_app(host, port, password, **kwargs)

    def init_app(self, host: str, port: int = 6379, password: Optional[str] = None, **kwargs):
        """
        Initialize or reinitialize the Redis client.
        
        :param host: Redis server hostname or IP
        :param port: Redis server port
        :param password: Optional password for authentication
        :param kwargs: Additional Redis settings (e.g., `db`, `decode_responses`, `socket_timeout`)
        """
        self.host = host
        self.port = port
        self.password = password

        # Create Redis client
        self.client = redis.Redis(host=host, port=port, password=password, **kwargs)

        # Optional: Test connection
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

        return self

    def set(self, key: str, value: str, ex: Optional[int] = None):
        """
        Set a key-value pair in Redis with an optional expiration time.

        :param key: Redis key
        :param value: Value to store
        :param ex: Expiration time in seconds (optional)
        """
        return self.client.set(key, value, ex=ex)

    def get(self, key: str) -> Optional[str]:
        """
        Get the value of a key from Redis.

        :param key: Redis key
        :return: Value as a string, or None if key does not exist
        """
        value = self.client.get(key)
        return value.decode() if value else None

    def delete(self, key: str):
        """Delete a key from Redis."""
        return self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        return self.client.exists(key) > 0

    def close(self):
        """Close the Redis connection."""
        if self.client:
            self.client.close()
