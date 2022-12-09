from fastapi import FastAPI
from app.routers import bus_locations, bus_stops, forecasts
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bus_locations.router, prefix="/buses", tags=["buses"])
app.include_router(bus_stops.router, prefix="/bus-stops", tags=["bus_stops"])
app.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])
