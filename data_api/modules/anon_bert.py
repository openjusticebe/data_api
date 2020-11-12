import logging
import re
import os
import json
import requests
from lib_misc import get_now
"""
Integrate with the anon bert container
"""

logger = logging.getLogger(__name__)

FAM2TYPE = {
    'PER': 'person',
    'LOC': 'place',
    'ORG': 'organization'
}


def run(text, params):
    entities = get_entities(text, params)

    log = []
    ent_types = {}
    for e in entities:
        log.append(f"Found \"{e['group']}\" ({e['family']})")
        if e['family'] == 'MISC':
            log.append("--> skipping")
            continue

        if e['family'] not in ent_types:
            ent_types[e['family']] = 1
        else:
            ent_types[e['family']] += 1

        index = ent_types[e['family']]

        text = re.sub(f"qu'(?={e['group']})", 'que ', text, flags=re.IGNORECASE)
        text = re.sub(f"d'(?={e['group']})", 'de ', text, flags=re.IGNORECASE)
        ttype = FAM2TYPE[e["family"]]
        title = f'{ttype}_{index}'
        print(f"'{e['group']}' / {e['family']} => {ttype} - {title}")
        if len(e['group']) > 2:
            #text = re.sub(f"(?P<pre>\W){e['group']}(?P<post>\W)", "\g<pre>coucou\g<post>", text, flags=re.IGNORECASE)
            text = re.sub(f"{e['group']}", f'<span class="pseudonymized {ttype} {title}">{title}</span>', text, flags=re.IGNORECASE)

    return text, log


def get_entities(text, params):
    host = os.getenv('ANON_BERT_HOST', 'http://localhost:8050')
    url = f"{host}/run"
    t = 0
    logging.debug("Anon_bert url: %s", url)
    req_data = {
        '_v': 1,
        '_timestamp': get_now(),
        'text': text,
        'params': json.dumps(params),
    }
    logging.debug("Anon_bert req: %s", req_data)
    while True:
        r = requests.post(url, json=req_data)
        if r.status_code == 200:
            break
        t += 1
        logging.debug("Attempt %s missed (status code: %s)", t, r.status_code)
        if t > 4:
            raise RuntimeError("Could not contact server")
    response_data = r.json()
    logging.debug("Entities: %s", response_data)
    return response_data['entities']
