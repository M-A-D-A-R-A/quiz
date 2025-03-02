from pydantic import BaseModel

class QuestionModel(BaseModel):
    question_id: str
    correct_city_id: int
    correct_obfuscated_id: str