import os
import json
import openai
from dotenv import load_dotenv
from supabase import create_client
import redis

load_dotenv()

# Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME", "default-bucket")

# Redis credentials from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)


# Set your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")
# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Redis client
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)



def generate_city_data(num_cities=5):
    """
    Generate sample city data with clues, fun facts, and trivia using OpenAI API.
    
    Args:
        num_cities: Number of cities to generate data for
        
    Returns:
        List of dictionaries containing the generated city data
    """
    # Example data to guide the generation
    example_data = [
        {
            "city": "Paris",
            "country": "France",
            "clues": [
                "This city is home to a famous tower that sparkles every night.",
                "Known as the 'City of Love' and a hub for fashion and art."
            ],
            "fun_fact": [
                "The Eiffel Tower was supposed to be dismantled after 20 years but was saved because it was useful for radio transmissions!",
                "Paris has only one stop sign in the entire city—most intersections rely on priority-to-the-right rules."
            ],
            "trivia": [
                "This city is famous for its croissants and macarons. Bon appétit!",
                "Paris was originally a Roman city called Lutetia."
            ]
        }
    ]
    
    # Construct the prompt
    system_message = "You are a helpful assistant that generates realistic and accurate sample data about cities around the world."
    
    user_message = f"""
    Generate data for {num_cities} different major cities around the world (choose diverse locations from different continents).
    Follow this exact format and structure for each city:
    
    ```
    [
      {{
        "city": "CityName",
        "country": "CountryName",
        "clues": [
          "A descriptive clue that hints at the city without naming it directly.",
          "Another clue about a famous landmark or cultural aspect of the city."
        ],
        "fun_fact": [
          "An interesting and surprising fact about the city that most people wouldn't know!",
          "Another lesser-known fact about the city's history or culture."
        ],
        "trivia": [
          "An entertaining piece of trivia about the city that would be interesting in a game.",
          "Another interesting trivia fact about the city."
        ]
      }},
      ...
    ]
    ```
    
    Provide ONLY the JSON array with no additional text or explanation.
    Be accurate with your facts but make them interesting and varied.
    """
    
    # Make the API call
    response = openai.chat.completions.create(
        model="gpt-4o",  # Use an appropriate model
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"}
    )
    
    # Extract and parse the response
    try:
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Handle different possible response formats
        if isinstance(data, dict) and "cities" in data:
            return data["cities"]
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, list):
            return data
        else:
            # If the API returns a nested object with a single key containing an array
            if isinstance(data, dict) and len(data) == 1 and isinstance(next(iter(data.values())), list):
                return next(iter(data.values()))
            return [data]
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response}")
        return []

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

def upload_to_supabase(file_path, bucket_name):
    """Uploads the JSON file to Supabase Storage if it doesn't exist and stores the URL in Redis."""
    existing_url = get_existing_file_url(file_path, bucket_name)
    if existing_url:
        # Store the existing URL in Redis for quick retrieval
        redis_client.set("latest_city_data_url", existing_url)
        return existing_url

    # Upload the file if it doesn’t exist
    with open(file_path, "rb") as file:
        response = supabase.storage.from_(bucket_name).upload(file_path, file, {"upsert": True})
    
    if "error" in response:
        print("Upload Failed:", response["error"])
        return None
    
    file_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_path}"
    print(f"File uploaded successfully: {file_url}")

    # Store the file URL in Redis for quick retrieval
    redis_client.set("latest_city_data_url", file_url)
    print("File URL stored in Redis.")

    return file_url




if __name__ == "__main__":
    try:
        city_data = generate_city_data(num_cities=4)
    except Exception as e:
        print(f"Error generating city data: {e}")
        file_path = "city_data.json"  # Path to local JSON file
        
         # Check if the file exists
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found!")
            exit(1)

        # Load city data from JSON file
        with open(file_path, "r") as f:
            city_data = json.load(f)
        
        print(f"Loaded data for {len(city_data)} cities from {file_path}.")


    

    print(f"Generated data for {len(city_data)} cities.")
    # Upload to Supabase Storage and store the link in Redis
    file_url = upload_to_supabase(file_path, BUCKET_NAME)
