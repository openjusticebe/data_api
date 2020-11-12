import logging
import re
import os
import requests
"""
Integrate with the anon etaamb container
"""

logger = logging.getLogger(__name__)


def run(text, params):
    lang = params.get('lang', 'french')
    log = []

    prepared_text = prepare(text)
    tokens = tokenize(prepared_text)
    scores = multi_score(lang, tokens)
    badtable = bad_tokens(scores)
    badcount = len(badtable)

    result = parse_text(text, badtable)

    msg = f"Token count: {len(tokens)}, masked: {badcount}"
    logger.debug(msg)
    log.append(msg)
    return result, log


def get_seq_scores(lang, tokenString):
    host = os.getenv('ANON_ETAAMB_HOST', 'http://localhost:8050')
    url = f"{host}/sequence_check"
    t = 0
    while True:
        r = requests.post(url, json={'lang': lang, 'string': tokenString})
        if r.status_code == 200:
            break
        t += 1
        if t > 4:
            raise RuntimeError("Could not contact server")
    return r.text


def prepare(text):
    # preg_replace('#<[^>]*>#Ui','',$text);
    text = re.sub(r'<[^>]*>', '', text)
    # preg_replace('#[^a-zA-Z\'\-À-ÿ]+#U',' ',$text);
    text = re.sub(r'[^a-zA-Z\'\-À-ÿ]+', ' ', text)
    return text


def tokenize(text):
    text = text.lower()
    tokens = list(set(re.compile("[^a-zA-ZÀ-ÿ]").split(text)))
    tokens = [s for s in tokens if s]
    tokens.sort()
    return tokens


def multi_score(lang, tokens):
    tokenString = ' '.join(tokens)
    scores = get_seq_scores(lang, tokenString).split(' ')
    result = {}
    for i, token in enumerate(tokens):
        result[token] = int(scores[i])
    return result


def bad_tokens(scores):
    return [(token, score) for token, score in scores.items() if score < 100]


def parse_text(text, badtable):
    for token, score in badtable:
        text = re.sub(token, '<span class="anonymized">****</span>', text, flags=re.IGNORECASE)
    return text
