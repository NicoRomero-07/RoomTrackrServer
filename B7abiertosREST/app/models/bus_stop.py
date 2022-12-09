from typing import List, Optional
from pydantic import BaseModel

from .nearby import Nearby


class BusRoute(BaseModel):
    codLinea: int
    userCodLinea: str
    nombreLinea: str
    cabeceraIda: str
    cabeceraVuelta: Optional[str]
    sentido: int
    orden: int
    nombreParada: str
    direccion: str
    lon: float
    lat: float


class BusStop(BaseModel):
    codParada: int
    total: int
    datos: List[BusRoute]


class NearbyBusStop(Nearby):
    datos: List[BusRoute]


class BusStopDetail(BaseModel):
    codParada: int
    nombreParada: str
    direccion: str
    latitud: float
    longitud: float


class BusStopTmp(BaseModel):
    parada: BusStopDetail
    sentido: int
    orden: int


class BusStopByLineCode(BaseModel):
    codLinea: float
    userCodLinea: str
    nombreLinea: str
    cabeceraIda: str
    cabeceraVuelta: str
    paradas: List[BusStopTmp]
