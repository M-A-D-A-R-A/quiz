from pydantic import BaseModel

class FunFactModel(BaseModel):
    city_id: int
    text: str

