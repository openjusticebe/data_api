#!/usr/bin/env python3
import argparse
import logging
import os
import toml
from datetime import datetime

import asyncpg
import pytz
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from pydantic import Json

from .routers import (
    collections,
    documents,
    users,
)

from .deps import (
    get_db,
    templates,
    logger,
)
from .lib_cfg import (config)
import data_api.deps as deps

import data_api.lib_misc as lm
from data_api.models import (
    # ListModel,
    ListTypes,
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
    {
        "name": "crud",
        "description": "Operations related to the creation, reading, update and deletion of documents (on a management level)"
    },
    {
        "name": "auth",
        "description": "Authentication may be required to access this endpoint"
    },
]
# ############################################ SERVER ROUTES
# #############################################################################


app = FastAPI(root_path=config.key('proxy_prefix'), openapi_tags=tags_metadata)
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Include sub routes
app.include_router(users.router)
app.include_router(collections.router)
app.include_router(documents.router)

# Server config
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
