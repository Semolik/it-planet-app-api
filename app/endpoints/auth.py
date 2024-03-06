from fastapi import APIRouter
from schemas.users import UserCreate, UserRead, UserReadAfterRegister
from users_controller import auth_backend, fastapi_users

api_router = APIRouter(prefix="/auth", tags=["auth"])

api_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/jwt"
)

api_router.include_router(
    fastapi_users.get_reset_password_router(),
)
api_router.include_router(
    fastapi_users.get_verify_router(UserReadAfterRegister)
)

api_router.include_router(
    fastapi_users.get_register_router(UserReadAfterRegister, UserCreate)
)
