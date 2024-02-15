from fastapi import FastAPI
from notifier import notifier
from utilities.files import init_folders
from db.init import init_superuser
from db.db import create_db_and_tables

from endpoints.auth import api_router as auth_router
from endpoints.users import api_router as users_router
from endpoints.files import api_router as files_router
from endpoints.locations import locations_router
from endpoints.verification import api_router as verification_router
from endpoints.hobbies import api_router as hobbies_router
from endpoints.likes import api_router as likes_router
from endpoints.chats import api_router as chats_router
from endpoints.messages import api_router as messages_router
from endpoints.notifications import api_router as notifications_router
from fastapi.middleware.cors import CORSMiddleware
import models_events
app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chats_router)
app.include_router(notifications_router)
app.include_router(messages_router)
app.include_router(likes_router)
app.include_router(files_router)
app.include_router(locations_router)
app.include_router(verification_router)
app.include_router(hobbies_router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await init_superuser()
    init_folders()
    await notifier.setup()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Set-Cookie"]
)
