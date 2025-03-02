import os
from functools import lru_cache
import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Load the .env file
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

class APISettings(BaseSettings):
    DEBUG = True

    JWT_ALGORITHM = "HS256"
    S3_PRE_SIGNED_DEFAULT_EXPIRY = 7200
    SYSTEM_IDENTITY = "headout"
    SECRET_KEY = "headout"
    BEARER_SYSTEM_JWT:str =''

    SUPABASE_URL=os.getenv("SUPABASE_URL")
    SUPABASE_KEY=os.getenv("SUPABASE_KEY")
    SUPABASE_BUCKET_NAME=os.getenv("SUPABASE_BUCKET_NAME")

    # Redis Credentials
    REDIS_HOST=os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT=os.getenv("REDIS_PORT", 6379)
    REDIS_PASSWORD=os.getenv("REDIS_PASSWORD")
    REDIS_KEY=os.getenv("REDIS_KEY")
    #COMMON
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return APISettings()
