import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from markdown2 import Markdown
from datetime import datetime
from ..models import (
    UpdateModel,
    SubmitModel,
    User,
)
from ..auth import (
    get_current_active_user_opt,
    credentials_exception,
    get_user_by_key,
)
from ..deps import (
    get_db,
    logger,
    doc_hash,
    templates,
)
from data_api.lib_parse import (
    convert
)

router = APIRouter()


# ############### CRUD
# ####################
@router.post("/create", tags=["crud"])
async def create(query: SubmitModel, request: Request, db=Depends(get_db)):
    """
    Submit document endpoint
    """
    logger.info('Testing user key %s', query.user_key)
    # FIXME : Fix airtable key checking
    rec = get_user_by_key(query.user_key)

    if not rec:
        raise HTTPException(status_code=401, detail="bad user key")

    ecli = f"ECLI:{query.country}:{query.court}:{query.year}:{query.identifier}"
    logger.info("User %s / %s submitting text %s", rec['username'], rec['email'], ecli)

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


@router.get("/d/read/{document_id}", tags=["crud"])
async def read(
        document_id: int,
        current_user: User = Depends(get_current_active_user_opt),
        db=Depends(get_db)):
    """
    Access to every detail about a document, so it contents
    can be reviewed, edited and validated.

    Admin user access required
    """
    if not current_user.admin:
        raise credentials_exception

    sql = """
    SELECT
        id_internal as id,
        ecli,
        country,
        court,
        year,
        identifier,
        text,
        meta->'labels' as labels,
        flags,
        date_created,
        lang,
        appeal,
        status,
        hash,
        date_created,
        date_updated,
        ukey
    FROM ecli_document
    WHERE id_internal = $1
    """

    doc_raw = await db.fetchrow(sql, document_id)
    user = get_user_by_key(doc_raw['ukey'])
    if not user:
        raise RuntimeError('Could not find user with key %s', doc_raw['ukey'])

    doc_data = {
        'id': doc_raw['id'],
        'ecli': doc_raw['ecli'],
        'country': doc_raw['country'],
        'court': doc_raw['court'],
        'year': doc_raw['year'],
        'identifier': doc_raw['identifier'],
        'text': doc_raw['text'],
        'labels': [] if doc_raw['labels'] is None else json.loads(doc_raw['labels']),
        'flags': doc_raw['flags'],
        'lang': doc_raw['lang'],
        'appeal': doc_raw['appeal'],
        'status': doc_raw['status'],
        'hash': doc_raw['hash'],
        'date_created': doc_raw['date_created'],
        'date_updated': doc_raw['date_updated'],
        'usermail': user.email,
        'username': user.name,
    }

    sql = """
    SELECT
        target_type as kind,
        target_identifier as link,
        target_label as label
    FROM ecli_links
    WHERE id_internal = $1
    """
    links_raw = await db.fetch(sql, document_id)
    links = [dict(x) for x in links_raw]

    doc_data['links'] = links

    return doc_data


@router.post("/d/update/{document_id}", tags=["crud"])
async def update(
        document_id: int,
        query: UpdateModel,
        current_user: User = Depends(get_current_active_user_opt),
        db=Depends(get_db)):
    """
    Update document endpoint
    """
    print("Update query received for document %s" % document_id)
    print(query)

    ecli = f"ECLI:{query.country}:{query.court}:{query.year}:{query.identifier}"

    meta = query.meta if query.meta is not None else {}
    meta['labels'] = query.labels

    sql = """
    UPDATE ecli_document
    SET
        ecli = $2,
        country = $3,
        court = $4,
        year = $5,
        identifier = $6,
        text = $7,
        meta = $8,
        lang = $9,
        appeal = $10,
        status = $11,
        date_updated = $12
    WHERE id_internal = $1
    """

    await db.execute(
        sql,
        document_id,
        ecli,
        query.country,
        query.court,
        query.year,
        query.identifier,
        query.text,
        json.dumps(meta),
        query.lang,
        query.appeal,
        query.status,
        datetime.now()
    )

    # Keep labels in database for reuse
    for label in query.labels:
        check = await db.fetchrow("SELECT 'one' FROM labels WHERE label = $1", label)
        if not check:
            logger.debug("New label : %s", label)
            await db.execute("INSERT INTO labels (label, category) VALUES ($1, 'user_defined')", label)

    # Store doclinks
    logger.debug("Removing doclinks for %s", document_id)
    await db.execute("DELETE FROM ecli_links WHERE id_internal = $1", document_id)
    logger.debug("Reinserting doclinks for %s", document_id)

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
            document_id,
            doc.kind,
            doc.link,
            doc.label,
        )

    # logger.debug('Wrote ecli %s ( hash %s ) to database', ecli, docHash)
    return {'result': "ok"}


# ############# ACCESS
# ####################
@router.get("/hash/{dochash}", response_class=HTMLResponse, tags=["access"])
async def view_html_hash(request: Request, dochash: str, db=Depends(get_db)):
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


@router.get("/html/{ecli}", response_class=HTMLResponse, tags=["access"])
async def view_html_ecli(request: Request, ecli, db=Depends(get_db)):
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


@router.get("/labels/{begin}", tags=["crud"])
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
