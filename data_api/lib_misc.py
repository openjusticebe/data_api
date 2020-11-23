import os
from datetime import datetime
import pytz
import calendar
import math

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

    res = await db.fetch(sql, country)

    if not res:
        raise RuntimeError("No results")

    return res['courts']


async def listYears(db, country, court):
    sql = """
    SELECT DISTINCT(year) AS years
    FROM ecli_document
    WHERE status = 'public'
    AND country = $1
    AND court = $2
    """

    res = await db.fetch(sql, country, court)

    if not res:
        raise RuntimeError("No results")

    return res['years']


async def listDocuments(db, country, court, year):
    sql = """
    SELECT identifier AS documents
    FROM ecli_document
    WHERE status = 'public'
    AND country = $1
    AND court = $2
    AND year = $3
    """

    res = await db.fetch(sql, country, court, year)

    if not res:
        raise RuntimeError("No results")

    return res['documents']
