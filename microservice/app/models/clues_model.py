from pydantic import BaseModel
class CluesModel(BaseModel):
    city_id: int
    text: str
