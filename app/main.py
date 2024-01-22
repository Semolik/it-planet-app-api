from fastapi import FastAPI
from utilities.files import init_folders
from db.init import init_superuser
from db.db import create_db_and_tables

from endpoints.auth import api_router as auth_router
from endpoints.users import api_router as users_router
from endpoints.files import api_router as files_router
import models_events
app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(files_router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await init_superuser()
    init_folders()
