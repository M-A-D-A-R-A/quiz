from pydantic import BaseModel

class AnswerRequest(BaseModel):
    question_id: str
    answer_id: str