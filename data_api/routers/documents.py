import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from datetime import datetime
from data_api.lib_cfg import config
from ..models import (
    UpdateModel,
    SubmitModel,
    User,
)
from ..auth import (
    get_current_active_user_opt,
    token_get_user,
    credentials_exception,
    get_user_by_key,
    get_user_by_email,
)
from ..deps import (
    get_db,
    logger,
    doc_hash,
    templates,
)
from ..lib_mail import notify
from data_api.lib_parse import (
    txt2html
)

router = APIRouter()


# ############### CRUD
# ####################
@router.post("/create", tags=["crud"])
async def create(
        query: SubmitModel,
        request: Request,
        current_user: User = Depends(get_current_active_user_opt),
        db=Depends(get_db)):

    """
    Submit document endpoint
    """

    if current_user:
        logger.info('User authentified %s', current_user.username)
        userRecord = current_user
    else:
        logger.info('Testing user key %s', query.user_key)
        userRecord = await get_user_by_key(query.user_key)

    if not userRecord:
        raise HTTPException(status_code=401, detail="bad user key")

    ecli = f"ECLI:{query.country}:{query.court}:{query.year}:{query.identifier}"
    logger.info("User %s / %s submitting text %s", userRecord.username, userRecord.email, ecli)

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
        userRecord.email,
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

    await notify(userRecord, 'create_doc', {'doc_hash': docHash})
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
        ukey,
        views_hash,
        views_public
    FROM ecli_document
    WHERE id_internal = $1
    """

    doc_raw = await db.fetchrow(sql, document_id)

    if '@' in doc_raw['ukey']:
        user = await get_user_by_email(doc_raw['ukey'])
    else:
        user = await get_user_by_key(doc_raw['ukey'])

    if not user:
        logger.error('Document %s error : empty user detected', doc_raw['id'])
        user = User(
            email='unknown@example.com',
            valid=False,
            username='unknown',
            admin=False
        )

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
        'username': user.username,
        'vhash': doc_raw['views_hash'],
        'vpublic': doc_raw['views_public'],
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

    if not current_user.admin:
        raise credentials_exception

    logger.info("Update query received for document %s" % document_id)
    ecli = f"ECLI:{query.country}:{query.court}:{query.year}:{query.identifier}"

    meta = query.meta if query.meta is not None else {}
    meta['labels'] = query.labels

    old_status = await db.fetchval(
        "SELECT status FROM ecli_document WHERE id_internal = $1",
        document_id)

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

    if old_status != query.status and query.status == 'public':
        ukey = await db.fetchval(
            "SELECT ukey FROM ecli_document WHERE id_internal = $1",
            document_id)
        user = await get_user_by_key(ukey)
        await notify(user, 'publish_doc', {'ecli': ecli})

    # logger.debug('Wrote ecli %s ( hash %s ) to database', ecli, docHash)
    return {'result': "ok"}


# ############# ACCESS
# ####################
@router.get("/hash/{dochash}", response_class=HTMLResponse, tags=["access"])
async def view_html_hash(
        request: Request,
        dochash: str,
        db=Depends(get_db),
        t: str = ''):

    """
    Access document with hash
    - If user is admin (token is provided and valid) : show document
    - If doc is published, redirect
    - If doc is hidden or new, and views level is ok : show document
    - Return error (access denied)
    """

    is_admin = False

    if t != '':
        try:
            user = token_get_user(t)
            is_admin = user.admin
        except Exception as e:
            logger.warning("User hash Token error")
            logger.exception(e)

    sql = """
    SELECT id_internal, ecli, text, appeal, meta->'labels' AS labels, views_hash, status
    FROM ecli_document
    WHERE hash = $1
    """

    res = await db.fetchrow(sql, dochash)

    if not res:
        raise HTTPException(status_code=404, detail="Document not found")

    if not is_admin:
        if res['status'] == 'public':
            ecli = res['ecli']
            return RedirectResponse(url=f'/html/{ecli}')
        if res['status'] == 'deleted':
            raise HTTPException(status_code=404, detail="Document not found")
        if res['status'] not in ('new', 'hidden'):
            raise HTTPException(status_code=423, detail="Content is locked")
        if res['views_hash'] > config.key('hash_max_views'):
            raise HTTPException(status_code=423, detail="Content is locked")
        await db.execute("UPDATE ecli_document SET views_hash = views_hash + 1 WHERE hash = $1", dochash)
    else:
        logger.info("Admin View enabled for %s", dochash)

    html_text = txt2html(res['text'])

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
        'hash': dochash,
        'ishash': True,
    })


@router.get("/html/{ecli}", response_class=HTMLResponse, tags=["access"])
async def view_html_ecli(request: Request, ecli, db=Depends(get_db)):
    # FIXME: add text output on request ACCEPT
    sql = """
    SELECT id_internal, ecli, text, appeal, meta->'labels' AS labels, hash
    FROM ecli_document
    WHERE ecli = $1
    AND status = 'public'
    """

    res = await db.fetchrow(sql, ecli)

    if not res:
        raise HTTPException(status_code=404, detail="Document not found")

    html_text = txt2html(res['text'])

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

    await db.execute("UPDATE ecli_document SET views_public = views_public + 1 WHERE ecli = $1", ecli)

    return templates.TemplateResponse('share.html', {
        'request': request,
        'ecli': res['ecli'],
        'text': html_text,
        'labels': json.loads(res['labels']) if res['labels'] else [],
        'appeal': res['appeal'],
        'elis': eli_links,
        'eclis': ecli_links,
        'hash': res['hash'],
        'ishash': False,
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
