import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from airtable import airtable
from markdown2 import Markdown
from data_api.models import (
    SubmitModel,
)

from ..deps import (
    config,
    get_db,
    logger,
    doc_hash,
    templates,
)
from data_api.lib_parse import (
    convert
)

router = APIRouter()


@router.post("/create", tags=["upload"])
async def create(query: SubmitModel, request: Request, db=Depends(get_db)):
    """
    Submit document endpoint
    """
    logger.info('Testing user key %s', query.user_key)
    # FIXME : Fix airtable key checking
    at = airtable.Airtable(config.key(['airtable', 'base_id']), config.key(['airtable', 'api_key']))
    res = at.get('Test Users', filter_by_formula="FIND('%s', {Key})=1" % query.user_key)
    ecli = f"ECLI:{query.country}:{query.court}:{query.year}:{query.identifier}"

    if res and 'records' in res and len(res['records']) == 1:
        rec = res['records'][0]['fields']
        logger.info("User %s / %s submitting text %s", rec['Name'], rec['Email'], ecli)
    else:
        raise HTTPException(status_code=401, detail="bad user key")

    meta = query.meta if query.meta is not None else {}
    meta['labels'] = query.labels

    docHash = doc_hash(ecli)

    sql = """
    INSERT INTO ecli_document (
        ecli,
        country,
        court,
        year,
        identifier,
        text,
        meta,
        ukey,
        lang,
        appeal,
        hash
    ) VALUES ( $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    RETURNING id_internal;
    """

    docId = await db.fetchval(
        sql,
        ecli,
        query.country,
        query.court,
        query.year,
        query.identifier,
        query.text,
        json.dumps(meta),
        query.user_key,
        query.lang,
        query.appeal,
        docHash,
    )

    # Keep labels in database for reuse
    for label in query.labels:
        check = await db.fetchrow("SELECT 'one' FROM labels WHERE label = $1", label)
        if not check:
            logger.debug("New label : %s", label)
            await db.execute("INSERT INTO labels (label, category) VALUES ($1, 'user_defined')", label)

    # Store doclinks
    for doc in query.doc_links:
        sql = """
            INSERT INTO ecli_links (
                id_internal,
                target_type,
                target_identifier,
                target_label
            ) VALUES ($1, $2, $3, $4);
        """

        await db.execute(
            sql,
            docId,
            doc.kind,
            doc.link,
            doc.label,
        )

    logger.debug('Wrote ecli %s ( hash %s ) to database', ecli, docHash)
    return {'result': "ok", 'hash': docHash}


@router.get("/hash/{dochash}", response_class=HTMLResponse, tags=["upload"])
async def gohash(request: Request, dochash: str, db=Depends(get_db)):
    sql = """
    SELECT id_internal, ecli, text, appeal, meta->'labels' AS labels
    FROM ecli_document
    WHERE hash = $1
    """

    res = await db.fetchrow(sql, dochash)

    if not res:
        raise HTTPException(status_code=404, detail="Document not found")

    markdowner = Markdown()
    html_text = markdowner.convert(
        res['text'].replace('_', '\\_')
    )
    html_text = convert(html_text)

    sql_links = """
    SELECT target_type, target_identifier, target_label
    FROM ecli_links
    WHERE id_internal = $1
    """

    res2 = await db.fetch(sql_links, res['id_internal'])
    ecli_links = []
    eli_links = []
    for row in res2:
        if row['target_type'] == 'ecli':
            ecli_links.append({'name': row['target_label'], 'id': row['target_identifier']})
        elif row['target_type'] == 'eli':
            eli_links.append({'name': row['target_label'], 'link': row['target_identifier']})

    return templates.TemplateResponse('share.html', {
        'request': request,
        'ecli': res['ecli'],
        'text': html_text,
        'labels': json.loads(res['labels']) if res['labels'] else [],
        'appeal': res['appeal'],
        'elis': eli_links,
        'eclis': ecli_links,
    })


@router.get("/html/{ecli}", response_class=HTMLResponse, tags=["upload"])
async def ecli(request: Request, ecli, db=Depends(get_db)):
    # FIXME: add text output on request ACCEPT
    sql = """
    SELECT id_internal, ecli, text, appeal, meta->'labels' AS labels
    FROM ecli_document
    WHERE ecli = $1
    AND status = 'public'
    """

    res = await db.fetchrow(sql, ecli)

    if not res:
        raise HTTPException(status_code=404, detail="Document not found")

    markdowner = Markdown()
    html_text = markdowner.convert(
        res['text'].replace('_', '\\_')
    )
    html_text = convert(html_text)

    sql_links = """
    SELECT target_type, target_identifier, target_label
    FROM ecli_links
    WHERE id_internal = $1
    """

    res2 = await db.fetch(sql_links, res['id_internal'])
    ecli_links = []
    eli_links = []
    for row in res2:
        if row['target_type'] == 'ecli':
            ecli_links.append({'name': row['target_label'], 'id': row['target_identifier']})
        elif row['target_type'] == 'eli':
            eli_links.append({'name': row['target_label'], 'link': row['target_identifier']})

    return templates.TemplateResponse('share.html', {
        'request': request,
        'ecli': res['ecli'],
        'text': html_text,
        'labels': json.loads(res['labels']) if res['labels'] else [],
        'appeal': res['appeal'],
        'elis': eli_links,
        'eclis': ecli_links,
    })


@router.get("/labels/{begin}", tags=["upload"])
async def labels(begin, db=Depends(get_db)):
    """
    Return matching labels (only search from beginning of string)
    """
    sql = """
    SELECT label FROM labels WHERE LOWER(label) LIKE $1 || '%'
    """

    res = await db.fetch(sql, begin.lower())

    output = []
    for row in res:
        output.append(row['label'])

    return output
