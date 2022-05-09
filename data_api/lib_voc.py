import logging
import httpx
import json
import time
from .lib_cfg import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('DEBUG'))
logger.addHandler(logging.StreamHandler())


async def getArkId(uri: str):
    logger.debug('Query new ark for %s', uri)
    # Mint ARK ID for uri
    #
    headers = {
        'Authorization': f'Bearer { config.key(["ark", "key"]) }',
        'Content-Type': 'application/json'
    }

    mint_payload = {
        'naan': config.key(['ark', 'naan']),
        'shoulder': f'/{ config.key(["ark", "shoulder"]) }',
        'url': uri,
        'metadata': {'msg': 'testing'},
        'maintenance_commitment': {},
    }

    i = 0
    while True:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f'{config.key(["ark", "url"])}/mint',
                    headers=headers,
                    content=json.dumps(mint_payload)
                )
                r.raise_for_status()
                data = r.json()
            break
        except Exception as e:
            i += 1
            if i > 3:
                logger.critical("Abandonning ark mint query, can't work it out")
                break
            logger.exception(e)
            time.sleep(1)

    return data.get('ark')


async def setArkUrl(ark: str, uri: str):
    logger.debug('Set ARK %s uri to %s', ark, uri)

    headers = {
        'Authorization': f'Bearer { config.key(["ark", "key"]) }',
        'Content-Type': 'application/json'
    }

    update_payload = {
        'ark': ark,
        'url': uri,
        'metadata': {'msg': 'testing'},
        'maintenance_commitment': {},
    }

    i = 0
    while True:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.put(
                    f'{config.key(["ark", "url"])}/update',
                    headers=headers,
                    content=json.dumps(update_payload)
                )
                r.raise_for_status()
            break
        except Exception as e:
            i += 1
            if i > 3:
                logger.critical("Abandonning ark update query, can't work it out")
                break
            logger.exception(e)
            time.sleep(1)

    return True


async def setLinks(docArk: str, termArks: list):
    logger.debug('Set Doc voc terms to %s', termArks)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f'{ config.key(["oj", "api", "auth"]) }/token',
            data={
                'username': config.key(['oj', 'user']),
                'password': config.key(['oj', 'pass']),
            }
        )
        r.raise_for_status()
        data = r.json()
    # Define links between docs and term arks

    headers = {
        'Authorization': f'Bearer { data.get("access_token") }',
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f'{ config.key(["oj", "api", "voc"]) }/link',
            headers=headers,
            content=json.dumps({'item_iri': docArk, 'terms': termArks})
        )
        r.raise_for_status()


async def getLinks(docArk: str):
    logger.debug('Get doc voc terms for %s', docArk)
    # Get voc terms associated with doc arks
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f'{ config.key(["oj", "api", "voc"]) }/link',
            params={'iri': docArk}
        )
        r.raise_for_status()
        print(r)
        data = r.json()
        print(data)

    return data.get('data', [])
