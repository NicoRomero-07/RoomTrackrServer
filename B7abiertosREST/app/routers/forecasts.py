from datetime import datetime
from typing import Union
from fastapi import APIRouter, HTTPException
import requests
from dotenv import dotenv_values
from app.utils.utils import check_time_format, get_day_forecast, get_opendata_json
from app.models.forecast import Forecast
import os

router = APIRouter()

#config = dotenv_values(".env")

config = os.environ

MALAGA_CODE = 29067
AEMET_BASE_URL = "https://opendata.aemet.es/opendata/api"
AEMET_DAILY_FORECAST_URL = f"{AEMET_BASE_URL}/prediccion/especifica/municipio/diaria/{MALAGA_CODE}"
AEMET_HOURLY_FORECAST_URL = f"{AEMET_BASE_URL}/prediccion/especifica/municipio/horaria/{MALAGA_CODE}"


def get_forecast(url: str):
    response = get_opendata_json(url, config['AEMET_API_KEY'])
    data_url = "datos"
    return requests.get(response[data_url]).json()


@router.get("", response_model=Forecast)
async def get_all_forecasts():
    daily_forecast = get_forecast(AEMET_DAILY_FORECAST_URL)
    return get_day_forecast(daily_forecast)[0]


@router.get("/today", response_model=Forecast)
async def get_today_forecasts():
    daily_forecast = get_forecast(AEMET_DAILY_FORECAST_URL)
    day = datetime.today().strftime('%Y-%m-%d')
    return get_day_forecast(daily_forecast, day)


@router.get("/{day}", response_model=Union[Forecast, dict])
async def get_forecast_by_day(day: str):
    try:
        check_time_format(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Incorrect date format.")

    daily_forecast = get_forecast(AEMET_DAILY_FORECAST_URL)

    return get_day_forecast(daily_forecast, day)
