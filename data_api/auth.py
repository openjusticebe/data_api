import asyncio
from typing import Optional

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from data_api.models import User

from .deps import logger, oj_code
from .lib_cfg import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=(config.key('token')), auto_error=False)

credentials_exception = HTTPException(
    status_code=(status.HTTP_401_UNAUTHORIZED),
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'}
)


async def get_user_by_key(user_key: str):
    logger.debug('Getting user from API, by key')
    url = '{host}/u/by/key'.format(host=(config.key('auth_host')))
    t = 0
    while True:
        r = requests.post(url, json={
            'key': oj_code(user_key),
            'env': config.key('oj_env')
        })
        if r.status_code == 200:
            break
        if r.status_code == 401:
            raise credentials_exception
        else:
            await asyncio.sleep(1)
            t += 1
        if t > 4:
            raise credentials_exception

    user = r.json()
    if user.get('valid') is not True:
        raise credentials_exception
    return User(**user)


async def get_user_by_email(user_email: str):
    logger.debug('Getting user from API, by email')
    url = '{host}/u/by/email'.format(host=(config.key('auth_host')))
    t = 0
    while True:
        r = requests.post(url, json={
            'email': oj_code(user_email),
            'env': config.key('oj_env')
        })
        if r.status_code == 200:
            break
        if r.status_code == 401:
            raise credentials_exception
        else:
            await asyncio.sleep(1)
            t += 1
        if t > 4:
            raise credentials_exception

    user = r.json()
    if user.get('valid') is not True:
        raise credentials_exception
    return User(**user)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        return False
    return await token_get_user(token)


async def token_get_user(token):
    logger.debug('Getting user data from API')
    url = '{host}/u/by/token'.format(host=(config.key('auth_host')))
    t = 0
    while True:
        r = requests.post(url, json={
            'token': oj_code(token),
            'env': config.key('oj_env')
        })
        if r.status_code == 200:
            break
        if r.status_code == 401:
            raise credentials_exception
        else:
            await asyncio.sleep(1)
            t += 1
        if t > 4:
            raise credentials_exception

    user = r.json()
    if user.get('valid') is not True:
        raise credentials_exception
    return User(**user)


def decode_token(token):
    raise RuntimeError('Obsolete')


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail='Could not identify user')
    if not current_user.valid:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


async def get_current_active_user_opt(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        return False
    if not current_user.valid:
        return False
    return current_user
