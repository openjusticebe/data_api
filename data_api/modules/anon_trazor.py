import logging
import re
import os
import random
from textrazor import TextRazor
"""
Integrate with the anon etaamb container
"""

logger = logging.getLogger(__name__)
MIN_SCORE = 0.1

FREEBASE_LOOKUP = {
    '/location/country': 'country',
    '/location/location': 'place',
    '/people/person': 'person',
    '/organization/organization': 'organization',
}

_COLORS = [
    '#ffb5e8',
    '#ff9cee',
    '#ffccf0',
    '#fcc2ff',
    '#f6a6ff',
    '#b28dff',
    '#c5a3ff',
    '#d5aaff',
    '#ecd4ff',
    '#fbe4ff',
    '#dcd3ff',
    '#a79aff',
    '#b5b9ff',
    '#97a2ff',
    '#afcbff',
    '#aff8db',
    '#c4faf8',
    '#85e3ff',
    '#ace7ff',
    '#6eb5ff',
    '#bffcc6',
    '#dbffd6',
    '#f3ffe3',
    '#e7ffac',
    '#ffffd1',
    '#ffc9de',
    '#ffabab',
    '#ffbebc',
    '#ffcbc1',
    '#fff5ba',
]


def api_keys():
    barrel = []
    for i in range(0, 3):
        keyname = f"TRAZOR_KEY_{i}"
        key = os.getenv(keyname)
        logger.info("Key %s: %s", keyname, key)
        if key:
            barrel.append(key)
    return barrel


def get_key(barrel, skip=False):
    return random.choice(barrel)


def run(text, params):
    entities = get_entities(text, params)
    log = []
    for e in entities:
        log.append(f"Found \"{e['id']}\" ({e['type']} #{e['index']}), score: {e['score']}")
        text = re.sub(f"qu'(?={e['text']})", 'que ', text, flags=re.IGNORECASE)
        text = re.sub(f"d'(?={e['text']})", 'de ', text, flags=re.IGNORECASE)
        title = f'{e["type"]}_{e["index"]}'
        text = re.sub(f"{e['text']}", f'<span class="pseudonymized {e["type"]} {title}">{title}</span>', text, flags=re.IGNORECASE)
    return text, log


def get_type(fb_types):
    for t in fb_types:
        if t in FREEBASE_LOOKUP:
            return FREEBASE_LOOKUP[t]
    return False


def get_entities(text, params):
    barrel = api_keys()
    client = TextRazor(get_key(barrel), extractors=["entities"])
    client.set_entity_allow_overlap = False
    response = client.analyze(text)

    if not response.ok:
        raise RuntimeError(response.error)

    entities = []
    ent_types = {}
    for e in response.entities():
        etype = get_type(e.freebase_types)
        if not etype:
            continue

        if etype not in ent_types:
            ent_types[etype] = 1
        else:
            ent_types[etype] += 1

        data = {
            'id': e.id,
            'words': e.matched_words,
            'text': e.matched_text,
            # 'score': e.relevance_score,
            'score': e.confidence_score,
            'type': etype,
            'index': ent_types[etype],
        }
        logger.debug(data)
        if data['score'] > MIN_SCORE and data['type']:
            entities.append(data)
    return entities
