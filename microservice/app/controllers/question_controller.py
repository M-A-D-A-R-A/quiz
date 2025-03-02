import fastapi
import json
import secrets

from fastapi import Request, HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi import Depends
from app.services.supabase_service import SupabaseApi
from app.services.redis_service import RedisApi
from ..config import get_settings
import random
from datetime import datetime, timezone, timedelta
import hashlib


from app.models.answer_model import AnswerRequest

router = fastapi.APIRouter(prefix="/headout")
supabase_service = SupabaseApi()
redis_service = RedisApi()

supabase_api = supabase_service.init_app(
    url=get_settings().SUPABASE_URL,
    key=get_settings().SUPABASE_KEY
)
redis_client = redis_service.init_app(
    host=get_settings().REDIS_HOST,
    port=get_settings().REDIS_PORT,
    password=get_settings().REDIS_PASSWORD
)

def clean_expired_questions():
    """Delete expired questions from Supabase (older than 30 minutes)"""
    try:
        expiry_threshold = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
        
        # Delete old questions from Supabase
        supabase_api.delete_data('questions', filters={'created_at': expiry_threshold})

        print("Expired questions cleaned from the database.")

    except Exception as e:
        print(f"Error cleaning expired questions: {e}")


@router.get('/api/stats')
# @token_required
def get_stats():
    """Get basic stats about the quiz database"""
    try:
        # Get counts from all tables
        cities_count = supabase_api.fetch_data('cities', count_exact=True)

        
        stats = {
            'total_cities': cities_count
        }
        
        return stats,200
    
    except Exception as e:
        print(f"Error getting stats: {e}")
        return HTMLResponse({'error': 'Failed to get stats'}), 500

@router.get('/api/questions')
# @token_required
async def get_question():
    """Get a random question with multiple choice answers"""
    try:
        
        # Get total cities count
        clean_expired_questions()
        total_cities = supabase_api.fetch_data('cities', count_exact=True)
        
        if total_cities == 0:
            return {'error': 'No cities in the database'}, 404
        
        # Get a random city ID
        # Since Supabase doesn't have a direct "ORDER BY RANDOM()" equivalent in the API,
        # we'll get all city IDs and select one randomly in Python
        cities_response = supabase_api.fetch_data('cities')
        all_city_ids = [city['id'] for city in cities_response.data]
        correct_city_id = random.choice(all_city_ids)
        # Get clues for the city
        clues_response = supabase_service.fetch_data(
            table="clues",
            columns="id, text",  # Fetch only 'id' and 'text'
            filters={"city_id": correct_city_id}
        )
        
        clues = clues_response.data
        
        if not clues:
            return {'error': 'No clues found for this city'}, 404
        
        # Randomly select 2 clues
        selected_clues = random.sample(clues, min(2, len(clues)))
        
        # Get correct city info
        city_response = supabase_api.fetch_data(
            table="cities",
            columns="id, name, country",  # Fetch only these columns
            filters={"id": correct_city_id}
        )
        correct_city = city_response.data[0] if city_response.data else None

        if not correct_city:
            return {'error': 'City not found'}, 404
        
        # Get 3 random incorrect cities
        # Again, we'll use Python to handle the randomization
        incorrect_cities = []
        available_ids = [city_id for city_id in all_city_ids if city_id != correct_city_id]
        
        if len(available_ids) >= 3:
            random_ids = random.sample(available_ids, 3)
            for city_id in random_ids:
                city_data = supabase_api.fetch_data(
                    table="cities",
                    columns="id, name, country",  # Fetch only these columns
                    filters={"id": city_id}
                )
                if city_data.data:
                    incorrect_cities.append(city_data.data[0])
        
        # Combine and shuffle all choices
        choices = [correct_city] + incorrect_cities
        random.shuffle(choices)

        city_choices = []
        correct_obfuscated_id = None

        for city in choices:
            obfuscated_id = hashlib.sha256(f"{city['id']}_{random.random()}".encode()).hexdigest()[:12]
            if city['id'] == correct_city_id:
                correct_obfuscated_id = obfuscated_id
            city_choices.append({
                'id': obfuscated_id,
                'name': f"{city['name']}, {city['country']}"
            })

        # Generate a unique question ID
        question_id = hashlib.sha256(f"question_{random.random()}".encode()).hexdigest()[:16]

        # Store the question in Redis (TTL: 30 minutes)
        question_data = {
            'question_id': question_id,
            'clues': [clue['text'] for clue in selected_clues],
            'choices': city_choices
        }
            # redis_client.setex(f"question:{question_id}", timedelta(minutes=30), json.dumps(question_data))
        insert_data = {
            'question_id': question_id,
        'correct_city_id': correct_city_id,
        'correct_obfuscated_id': correct_obfuscated_id,
        'clues': question_data['clues'],  # Store as TEXT[]
        'choices': json.dumps(question_data['choices']),  # Store as JSONB
        'created_at': datetime.now(timezone.utc).isoformat()
        }
        redis_client.set(f"question:{question_id}", json.dumps(insert_data))

        # Store question in the database (optional for persistence)
        supabase_api.insert_data('questions', {
            'question_id': question_id,
        'correct_city_id': correct_city_id,
        'correct_obfuscated_id': correct_obfuscated_id,
        'clues': question_data['clues'],  # Store as TEXT[]
        'choices': json.dumps(question_data['choices']),  # Store as JSONB
        'created_at': datetime.now(timezone.utc).isoformat()
        })

        return question_data
        
        # # Format the response
        # response = {
        #     'question_id': correct_city_id,
        #     'clues': [clue['text'] for clue in selected_clues],
        #     'choices': [{'name': f"{choice['name']}, {choice['country']}"} for choice in choices]
        # }
        
        # return response,200
    
    except Exception as e:
        print(f"Error getting question: {e}")
        return {'error': 'Failed to get question'}, 500

@router.post('/api/answer')
async def check_answer(data: AnswerRequest =Depends()):
    """
    Check if the submitted answer is correct.
    """
    try:
        # Compare question_id and answer_id
        question_id = data.question_id
        answer_id = data.answer_id

        clean_expired_questions()
        question_data_json = redis_client.get(f"question:{question_id}")

        if question_data_json:
            print("Cache hit: Fetching from Redis")
            try:
                question_data = json.loads(question_data_json)  # Convert string to dict
            except json.JSONDecodeError:
                print("Error decoding JSON from Redis")
                question_data = None
        else:
            question_data = None

        # If Redis cache is empty or corrupted, fetch from Supabase
        if not question_data:
            print("Cache miss: Fetching from Supabase")
            response = supabase_api.fetch_data(table="questions", filters={"question_id": question_id})

            if not response or not response.data:  # Handle empty response
                print("Question not found in Supabase")
                return None  # Return None if no data

            question_data = response.data[0]  # Extract first row

            # Store in Redis for future use (TTL = 30 min)

        # Extract required fields safely
        correct_city_id = question_data.get("correct_city_id")
        correct_obfuscated_id = question_data.get("correct_obfuscated_id")


        
        # Check if the answer is correct
        is_correct = (answer_id == correct_obfuscated_id)
        # Get city details
        city_response = supabase_api.fetch_data(table="cities", filters={"id": correct_city_id})
        city = city_response.data[0] if city_response.data else None

        if not city:
            raise HTTPException(status_code=404, detail="City not found")

        # Get a random fun fact about the city
        fun_facts_response = supabase_api.fetch_data(table="fun_facts", filters={"city_id": correct_city_id})
        fun_facts = fun_facts_response.data
        
        fun_fact = random.choice(fun_facts)["text"] if fun_facts else "No fun facts available for this city."

        return {
            "correct": is_correct,
            "city": f"{city['name']}, {city['country']}",
            "fun_fact": fun_fact
        }

    except Exception as e:
        print(f"Error checking answer: {e}")
        raise HTTPException(status_code=500, detail="Failed to check answer")