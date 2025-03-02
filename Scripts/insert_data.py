import json
import os
import redis
from dotenv import load_dotenv
from supabase import create_client
from urllib.parse import urlparse
import requests

load_dotenv()
# Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME", "default-bucket")

# Redis credentials from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_KEY = os.getenv("REDIS_KEY", None)

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Redis client
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

# Get storage file path from Redis
def get_file_path_from_redis(redis_key):
    file_path = redis_client.get(redis_key)
    if not file_path:
        raise Exception(f"File path not found in Redis for key: {redis_key}")
    return file_path


def get_existing_file_url(file_path, bucket_name):
    """Checks if the file already exists in Supabase Storage and returns its URL."""
    try:
        response = supabase.storage.from_(bucket_name).list()
        existing_files = [file["name"] for file in response if "name" in file]
        
        if file_path in existing_files:
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_path}"
            print(f"File already exists: {file_url}")
            return file_url
    except Exception as e:
        print("Error checking existing files:", e)
    
    return None

def fetch_data_from_supabase(url: str):
    """Fetches data from a given Supabase storage URL and returns the JSON content."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()  # Return JSON content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    

# Get JSON file from Supabase Storage using path from Redis
def get_json_from_storage(bucket_name, redis_key,file_path):
    # Get file path from Redis
    file_path_from_redis = get_file_path_from_redis(redis_key)
    if not file_path_from_redis:
        # Download file from Supabase storage
        file_url = get_existing_file_url(file_path, bucket_name)
        if not file_url:
            raise Exception(f"File not found in Supabase Storage for path: {file_path}")
        
        response = fetch_data_from_supabase(file_url)
        
        return response
    
    else:
        response = fetch_data_from_supabase(file_path_from_redis)
        return response

# Insert data into tables
def insert_data(data):
    # Process each city
    for city_data in data:
        # Insert city
        city_result = supabase.table("cities").insert({
            "name": city_data["city"],
            "country": city_data["country"]
        }).execute()
        
        city_id = city_result.data[0]['id']
        
        # Insert clues
        for clue in city_data["clues"]:
            supabase.table("clues").insert({
                "city_id": city_id,
                "text": clue
            }).execute()
        
        # Insert fun facts
        for fact in city_data["fun_fact"]:
            supabase.table("fun_facts").insert({
                "city_id": city_id,
                "text": fact
            }).execute()
        
        # Insert trivia
        for trivia in city_data["trivia"]:
            supabase.table("trivia").insert({
                "city_id": city_id,
                "text": trivia
            }).execute()
    
    print("Data import completed successfully!")

# Main execution
if __name__ == "__main__":
    # Replace with your actual bucket name and Redis key
    file_path =  "city_data.json" 
    try:
        # Get data from storage using path stored in Redis
        cities_data = get_json_from_storage(BUCKET_NAME, REDIS_KEY,file_path)

        # Insert data into tables   
        insert_data(cities_data)
        
    except Exception as e:
        print(f"Error during data import: {e}")
    finally:
        # Close Redis connection
        redis_client.close()