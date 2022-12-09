from typing import List, Union, Optional
from fastapi import APIRouter, HTTPException
from app.models.bus import Bus, BusFilter, NearbyBus
from app.utils.utils import format_nearby_data_json, get_json_by_field, get_opendata_json, is_crs, proximity_search_buses
import pandas as pd

router = APIRouter()
BUS_RESOURCES_URL = "https://datosabiertos.malaga.eu/recursos/transporte/EMT"
BUS_LOCATION_GEOJSON_URL = f"{BUS_RESOURCES_URL}/EMTlineasUbicaciones/lineasyubicaciones.geojson"


def setup_geojson_dataframe():
    df = pd.read_json(BUS_LOCATION_GEOJSON_URL)
    df["lastUpdate"] = df["properties"].apply(lambda x: x["last_update"])

    return df


@router.get("", response_model=List[Bus])
async def get_all_bus_location():
    return get_opendata_json(BUS_LOCATION_GEOJSON_URL)


@router.get("/search/nearby", response_model=NearbyBus)
async def get_nearby_buses(lat: float, lon: float, radius: Optional[int] = 500):
    if not is_crs(lat, lon):
        raise HTTPException(
            status_code=400, detail="Coordinates out of range.")
    df = setup_geojson_dataframe()
    df = proximity_search_buses(df, lat, lon, radius)

    return format_nearby_data_json(df, lat, lon, radius)


@router.get("/search", response_model=Union[BusFilter, dict])
async def get_location_by_line_code(line_code: str):
    df = setup_geojson_dataframe()
    line_code_field = "codLinea"

    result = get_json_by_field(df, line_code_field, float(line_code))

    return next(iter(result), {})


@router.get("/{bus_code}", response_model=Union[BusFilter, dict])
async def get_location_by_bus_code(bus_code: int):
    df = setup_geojson_dataframe()
    bus_code_field = "codBus"
    result = get_json_by_field(df, bus_code_field, bus_code)

    return next(iter(result), {})
