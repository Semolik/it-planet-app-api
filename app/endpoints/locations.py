from endpoints.locations_endpoints import cities
from fastapi import APIRouter
locations_router = APIRouter(prefix="/locations")
locations_router.include_router(cities.api_router)
