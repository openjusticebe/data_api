#!/usr/bin/env python3
import argparse
import logging
import os
import toml
from airtable import airtable
from datetime import datetime, timedelta
import yaml

import asyncpg
import pytz
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import Json
from typing import Optional
from jose import JWTError, jwt

from .routers import collections, upload
from .deps import (
    get_db,
    templates,
    logger,
    verify_password,
)
from .lib_cfg import (
    config,
)
import data_api.deps as deps

import data_api.lib_misc as lm
from data_api.models import (
    # ListModel,
    ListTypes,
    Token,
    TokenData,
    User,
)


# ################################################### SETUP AND ARGUMENT PARSING
# ##############################################################################
dir_path = os.path.dirname(os.path.realpath(__file__))


VERSION = 4
START_TIME = datetime.now(pytz.utc)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

tags_metadata = [
    {
        "name": "users",
        "description": "Operations related to users"
    },
    {
        "name": "authentication",
        "description": "Login, logout, etc."
    },
    {
        "name": "collections",
        "description": "Operations on collections, depending authentified user"
    },
    {
        "name": "upload",
        "description": "Operations related to the upload of documents"
    },
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=config.key('token'))


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

# ############################################ SERVER ROUTES
# #############################################################################


app = FastAPI(root_path=config.key('proxy_prefix'), openapi_tags=tags_metadata)
app.mount("/static", StaticFiles(directory="./static"), name="static")
app.include_router(collections.router)
app.include_router(upload.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    if os.getenv('NO_ASYNCPG', 'false') == 'false':
        try:
            cfg = config.key('postgresql')
            deps.DB_POOL = await asyncpg.create_pool(**cfg)
        except asyncpg.InvalidPasswordError:
            if config.key('log_level') != 'debug':
                logger.critical("No database found")
                raise
            logger.warning("No Database Found !!!! But we're in debug mode, proceeding anyway")
            deps.DB_POOL = False
# ############################################################### SERVER ROUTES
# #############################################################################


@app.get("/")
def root():
    return lm.status_get(START_TIME, VERSION)


@app.get("/list")
async def getList(request: Request, db=Depends(get_db), level: ListTypes = 'country', data: Json = {}):
    """
    List available data according to query
    """
    if level not in ListTypes._member_names_:
        raise HTTPException(status_code=400, detail="Bad Request")

    try:
        if level == ListTypes.country:
            response = 'BE'

        if level == ListTypes.court:
            response = await lm.listCourts(db, data['country'])

        if level == ListTypes.year:
            response = await lm.listYears(db, data['country'], data['court'])

        if level == ListTypes.document:
            response = await lm.listDocuments(db, data['country'], data['court'], data['year'])

        if not isinstance(response, list):
            return [response]
        return response

    except KeyError:
        raise HTTPException(status_code=417, detail="Missing data")
    except RuntimeError:
        raise HTTPException(status_code=404, detail="Not Found")


@app.get("/test", response_class=HTMLResponse)
def test(request: Request, ):
    """
    Simple HTML output simulation
    """
    return templates.TemplateResponse('share.html', {
        'request': request,
        'ecli': 'test',
        'text': 'Ceci est un test',
        'labels': ['test1', 'test2'],
        'elis': [],
        'eclis': [],
    })


@app.post("/token", response_model=Token)
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


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# ##################################################################### STARTUP
# #############################################################################
def main():
    parser = argparse.ArgumentParser(description='Matching server process')
    parser.add_argument('--config', dest='config', help='config file', default=None)
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    # XXX: Lambda is a hack : toml expects a callable
    if args.config:
        t_config = toml.load(['config_default.toml', args.config])
    else:
        t_config = toml.load('config_default.toml')

    config.merge(t_config)

    if args.debug:
        logger.setLevel(logging.getLevelName('DEBUG'))
        logger.debug('Debug activated')
        config.set('log_level', 'debug')
        config.set(['server', 'log_level'], 'debug')
        logger.debug('Arguments: %s', args)
        config.dump()
        # logger.debug('config: %s', toml.dumps(config))

        # uvicorn.run(
        #     "data_api.main:app",
        #     reload=True,
        #     **config.key('server')
        # )
    uvicorn.run(
        app,
        **config.key('server')
    )


if __name__ == "__main__":
    main()
