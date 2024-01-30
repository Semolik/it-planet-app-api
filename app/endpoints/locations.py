from endpoints.locations_endpoints import cities
from endpoints.locations_endpoints import institutes
from endpoints.locations_endpoints import universities
from fastapi import APIRouter
locations_router = APIRouter(prefix="/locations")
locations_router.include_router(cities.api_router)
locations_router.include_router(institutes.api_router)
locations_router.include_router(universities.api_router)
