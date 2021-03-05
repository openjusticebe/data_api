import calendar
import math
import os
from datetime import datetime

import pytz

COUNTER = 0


def check_envs(env_list):
    return all(os.getenv(e) for e in env_list)


def get_now():
    now = datetime.now(pytz.utc)
    return calendar.timegm(now.utctimetuple())


def status_get(start_time, version):
    now = datetime.now(pytz.utc)
    delta = now - start_time
    delta_s = math.floor(delta.total_seconds())
    return {
        'all_systems': 'nominal',
        'id': __name__,
        'timestamp': str(now),
        'online_since': str(start_time),
        'online_for_seconds': delta_s,
        'api_version': version,
        'api_counter': COUNTER,
    }


async def listCourts(db, country):
    sql = """
    SELECT DISTINCT(court) AS courts
    FROM ecli_document
    WHERE status = 'public'
    AND country = $1
    """

    rows = await db.fetch(sql, country)

    if not rows:
        raise RuntimeError("No results")

    return [x['courts'] for x in rows]


async def listYears(db, country, court):
    sql = """
    SELECT DISTINCT(year) AS years
    FROM ecli_document
    WHERE status = 'public'
    AND country = $1
    AND court = $2
    """

    rows = await db.fetch(sql, country, court)

    if not rows:
        raise RuntimeError("No results")

    return [x['years'] for x in rows]


async def listDocuments(db, country, court, year):
    sql = """
    SELECT identifier AS documents
    FROM ecli_document
    WHERE status = 'public'
    AND country = $1
    AND court = $2
    AND year = $3
    """

    rows = await db.fetch(sql, country, court, year)

    if not rows:
        raise RuntimeError("No results")

    return [x['documents'] for x in rows]
