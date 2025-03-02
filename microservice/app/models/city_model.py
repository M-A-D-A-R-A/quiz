from pydantic import BaseModel

class CityModel(BaseModel):
    name: str
    country: str



