from math import radians, cos, sin, asin, sqrt
import json
import pandas as pd
from requests.exceptions import Timeout
from requests import HTTPError, ConnectionError
import requests
from typing import List, Optional
from datetime import datetime


def get_opendata_json(url: str, api_key: Optional[str] = None):
    try:
        if api_key:
            req = requests.get(url, headers={"api_key": api_key})
        else:
            req = requests.get(url)
    except HTTPError:
        print("An HTTP error occurred.")
    except Timeout:
        print("Time out exception.")
    except ConnectionError:
        print("Connection error.")

    return req.json()


def check_time_format(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Calculate the great circle distance in meters between two points
    on the earth (specified in decimal degrees)
    """
    METER_TO_KM = 1000
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    r = 6371

    return c * r * METER_TO_KM


def _to_dict(row, name):
    res = {}
    value = ""
    for i, r in enumerate(row):
        if (row.index[i] != name):
            res[row.index[i]] = r
        else:
            value = r
    return pd.Series({name: value, "resultados": res})


def get_json_by_field(df: pd.DataFrame, field_name: str, field_value: str):
    df = df[df[field_name] == field_value]
    if not df.empty:
        df = df.apply(lambda row: _to_dict(row, field_name), axis=1)
        df = df.groupby([field_name], as_index=False).agg(total=pd.NamedAgg(column="resultados", aggfunc="count"),
                                                          datos=pd.NamedAgg(column="resultados", aggfunc=list))
    df = df.to_json(force_ascii=False, orient="records")
    return json.loads(df)


def proximity_search_stops(df: pd.DataFrame, lat: float, lon: float, radius: int):
    return df[df.apply(lambda x: haversine_distance(
        x["lat"], x["lon"], lat, lon) <= radius, axis=1)]


def proximity_search_buses(df: pd.DataFrame, lat: float, lon: float, radius: int):
    df = df[df.apply(lambda x: haversine_distance(
        float(x["geometry"]["coordinates"][1]), float(x["geometry"]["coordinates"][0]), lat, lon) <= radius, axis=1)]
    if not df.empty:
        distance = df.apply(lambda row: haversine_distance(float(
            row["geometry"]["coordinates"][1]), float(row["geometry"]["coordinates"][0]), lat, lon), axis=1)
        df = df.assign(distancia=distance)
    return df


def format_nearby_data_json(df: pd.DataFrame, lat: float, lon: float, radius: int):
    json_data = df.to_json(force_ascii=False, orient="records")
    filtered_data = json.loads(json_data)

    return {"lat": lat, "lon": lon, "radius": radius, "total": len(filtered_data), "datos": filtered_data}


def filter_forecast_by_hour(forecast: List[dict], hour: str):
    for field in forecast:
        for f in forecast[field]:
            if (type(f) == dict):
                for key in f:
                    if (key == "periodo" and int(f[key]) == int(hour)):
                        forecast[field] = f
    return forecast


def get_day_forecast(daily_forecast: List[dict], day: str = None):
    forecasts = daily_forecast[0]["prediccion"]["dia"]
    result = forecasts
    if day:
        result = next(
            (f for f in forecasts if f["fecha"] == f"{day}T00:00:00"), {})

    return result


def is_crs(lat: float, lon: float) -> bool:
    MAX_LON = 180
    MAX_LAT = 90

    return abs(lat) < MAX_LAT and abs(lon) < MAX_LON
