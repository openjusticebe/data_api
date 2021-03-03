import random
import logging
import os
from datetime import datetime
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from fastapi import Header, HTTPException
from .lib_cfg import config
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())

templates = Jinja2Templates(directory="templates")
jinjaEnv = Environment(
    loader=FileSystemLoader('%s/../templates/' % os.path.dirname(__file__)))

DB_POOL = False


async def get_token_header(x_token: str = Header(...)):
    if x_token != config.key('token'):
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


async def get_db():
    global DB_POOL  # pylint:disable=global-statement
    conn = await DB_POOL.acquire()
    try:
        yield conn
    finally:
        await DB_POOL.release(conn)


@asynccontextmanager
async def oj_db():
    global DB_POOL  # pylint:disable=global-statement
    conn = await DB_POOL.acquire()
    try:
        yield conn
    finally:
        await DB_POOL.release(conn)


def doc_hash(ecli):
    nonce = random.randint(0, 99999999)
    num = hex(abs(hash(F"{ecli}{nonce}{config.key('salt')}{datetime.now()}")))
    return num.lstrip("0x").rstrip("L")
