from fastapi import APIRouter

router = APIRouter()


@router.get("/auth/", tags=["authentication"])
async def auth():
    return []


@router.get("/u/", tags=["users"])
async def read_users():
    return []


@router.get("/u/me", tags=["users"])
async def read_user_me():
    return {
    }


@router.get("/u/{username}", tags=["users"])
async def read_user(username: str):
    return {
        "username": username
    }
