from fastapi import APIRouter, Depends
from data_api.models import (
    User,
)
from data_api.auth import (
    get_current_active_user,
)

router = APIRouter()


@router.get("/u/", tags=["users"])
async def read_users():
    return []


@router.get("/u/me", response_model=User, tags=["users"])
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    """
    Read data from connected user
    """
    return current_user


@router.get("/u/{username}", tags=["users"])
async def read_user(username: str):
    return {
        "username": username
    }
