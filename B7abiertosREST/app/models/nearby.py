from pydantic import BaseModel


class Nearby(BaseModel):
    lat: float
    lon: float
    radius: int
    total: int
