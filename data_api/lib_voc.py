import logging
from .lib_cfg import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('DEBUG'))
logger.addHandler(logging.StreamHandler())


async def getArkId(uri: str):
    logger.debug('Query new ark for %s', uri)
    # Mint ARK ID for uri
    pass


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
