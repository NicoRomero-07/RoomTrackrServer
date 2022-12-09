from typing import List, Optional
from pydantic import BaseModel, validator

from app.models.nearby import Nearby


class Geometry(BaseModel):
    type: str
    coordinates: List[float]

    @validator("coordinates")
    def check_coordinates_length(cls, v):
        if len(v) != 2:
            raise ValueError("Wrong coordinates format.")
        return v


class BusProperty(BaseModel):
    codLinea: str
    codBus: str
    sentido: str
    codParIni: int
    last_update: str


class Bus(BaseModel):
    geometry_name: Optional[str]
    geometry: Geometry
    codBus: Optional[str]
    codLinea: Optional[str]
    sentido: str
    type: str
    properties: Optional[BusProperty]


class NearbyBus(Nearby):
    datos: List[Bus]


class BusFilter(BaseModel):
    codLinea: Optional[int]
    codBus: Optional[int]
    total: int
    datos: List[Bus]
