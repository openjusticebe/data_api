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
                    config.key(["ark", "url"]),
                    headers=headers,
                    content=json.dumps(mint_payload)
                )
                r.raise_for_status()
                data = r.json()
            break
        except Exception as e:
            i += 1
            if i > 3:
                logger.critical("Abandonning ark query, can't work it out")
                break
            logger.exception(e)
            time.sleep(1)

    return data.get('ark')


async def setArkUrl(ark: str, uri: str):
    logger.debug('Set ARK %s uri to %s', ark, uri)
    # Set ARK url for ark id
    pass


async def setLinks(docArk: str, termArks: list):
    logger.debug('Set Doc voc terms to %s', termArks)
    # Define links between docs and term arks
    pass


async def getLinks(docArk: str):
    logger.debug('Get doc voc terms for %s', docArk)
    # Get voc terms associated with doc arks
    pass
