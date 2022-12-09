from typing import List
from pydantic import BaseModel


class Data(BaseModel):
    value: str


class PeriodData(Data):
    periodo: str


class HourData(Data):
    hora: int


class WindData(BaseModel):
    direccion: str
    velocidad: int


class MinMaxData(BaseModel):
    maxima: int
    minima: int
    dato: List[HourData]


class SkyData(PeriodData):
    descripcion: str


class Forecast(BaseModel):
    uvMax: int
    fecha: str
    humedadRelativa: MinMaxData
    sensTermica: MinMaxData
    temperatura: MinMaxData
    rachaMax: List[PeriodData]
    viento: List[WindData]
    estadoCielo: List[SkyData]
    cotaNieveProv: List[PeriodData]
    probPrecipitacion: List[PeriodData]
