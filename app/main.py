from fastapi import FastAPI
from utilities.files import init_folders
from db.init import init_superuser
from db.db import create_db_and_tables

from endpoints.auth import api_router as auth_router
from endpoints.users import api_router as users_router
from endpoints.files import api_router as files_router
from endpoints.locations import locations_router
from endpoints.verification import api_router as verification_router
import models_events
app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(locations_router)
app.include_router(verification_router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await init_superuser()
    init_folders()
