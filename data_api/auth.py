import logging
import yaml
from jose import JWTError, jwt
from airtable import airtable
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta
from .lib_cfg import (
    config,
)
from data_api.models import (
    TokenData,
    User,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=config.key('token'))


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def auth_user(username: str, password: str):
    at = airtable.Airtable(config.key(['airtable', 'base_id']), config.key(['airtable', 'api_key']))
    res = at.get('Test Users', filter_by_formula="FIND('%s', {Email})=1" % username)
    try:
        rec = res['records'][0]['fields']
        assert verify_password(password, rec['pass'])
        logger.info("Authentified user %s", rec['Name'])
        udict = {
            'email': rec['Email'],
            'valid': rec['Valid'],
            'username': rec['Name'],
        }
        logger.debug(yaml.dump(rec, indent=2))
        return User(**udict)
    except (KeyError, AssertionError):
        logger.info('Error occured')
        logger.debug(res)
        return None


def get_user(username: str):
    at = airtable.Airtable(config.key(['airtable', 'base_id']), config.key(['airtable', 'api_key']))
    logger.info('Checking for %s in db', username)
    res = at.get('Test Users', filter_by_formula="FIND('%s', {Email})=1" % username)
    try:
        rec = res['records'][0]['fields']
        udict = {
            'email': rec['Email'],
            'valid': rec['Valid'],
            'username': rec['Name'],
        }
        return User(**udict)
    except (KeyError, AssertionError):
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.key(['auth', 'secret_key']),
        algorithm=config.key(['auth', 'algorithm'])
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.key(['auth', 'secret_key']), algorithms=[config.key(['auth', 'algorithm'])])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.valid:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
