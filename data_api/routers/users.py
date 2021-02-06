from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from data_api.lib_cfg import config
from data_api.models import (
    Token,
    User,
)
from data_api.auth import (
    auth_user,
    create_access_token,
    get_current_active_user,
)

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authentify users
    """
    # FIXME: Some other auth provider then airtable would be nice
    # FIXME: Add support for scopes (like admin, moderatore, ...)
    # FIXME: Add password hashing support
    user = auth_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.key(['auth', 'expiration_minutes']))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user

@router.get("/auth/", tags=["authentication"])
async def auth():
    return []


@router.get("/u/", tags=["users"])
async def read_users():
    return []


@router.get("/u/me", response_model=User, tags=["users"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/u/{username}", tags=["users"])
async def read_user(username: str):
    return {
        "username": username
    }
