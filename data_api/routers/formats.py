import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from data_api.lib_cfg import config
from ..deps import (
    get_db,
    logger,
    doc_hash,
    templates,
)
from starlette.requests import Request
from data_api.lib_parse import (
    md2latex,
    latex2pdf,
)
from ..auth import (
    token_get_user,
)

router = APIRouter()


async def check_access(t, status, db, dochash, views_hash):
    is_admin = False

    if t != '':
        try:
            user = token_get_user(t)
            is_admin = user.admin
        except Exception as e:
            logger.warning("User hash Token error")
            logger.exception(e)

    if not is_admin:
        if status == 'public':
            pass
        elif status == 'deleted':
            raise HTTPException(status_code=404, detail="Document not found")
        elif status not in ('new', 'hidden'):
            raise HTTPException(status_code=423, detail="Content is locked")
        elif views_hash > config.key('hash_max_views'):
            raise HTTPException(status_code=423, detail="Content is locked")
        else:
            await db.execute("UPDATE ecli_document SET views_hash = views_hash + 1 WHERE hash = $1", dochash)

# ############## ROUTE
# ####################


@router.get("/d/pdf/{dochash}", tags=["access"])
async def view_pdf_hash(
        request: Request,
        dochash: str,
        db=Depends(get_db),
        t: str = ''):

    sql = """
    SELECT id_internal, identifier, ecli, text, appeal, meta->'labels' AS labels, views_hash, status
    FROM ecli_document
    WHERE hash = $1
    """

    res = await db.fetchrow(sql, dochash)
    if not res:
        raise HTTPException(status_code=404, detail="Document not found")
    else:
        await check_access(t, res['status'], db, dochash, res['views_hash'])

    latex = md2latex({
        'body': res['text'],
        'title': res['ecli'],
    })
    fname = re.sub(r'[\W_]+', '-', res['identifier'])
    return Response(
        content=latex2pdf(latex),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{fname}.pdf\""}
    )


@router.get("/d/txt/{dochash}", response_class=PlainTextResponse, tags=["access"])
async def view_pdf_hash(
        request: Request,
        dochash: str,
        db=Depends(get_db),
        t: str = ''):

    sql = """
    SELECT id_internal, ecli, text, appeal, meta->'labels' AS labels, views_hash, status
    FROM ecli_document
    WHERE hash = $1
    """

    res = await db.fetchrow(sql, dochash)
    if not res:
        raise HTTPException(status_code=404, detail="Document not found")
    else:
        await check_access(t, res['status'], db, dochash, res['views_hash'])

    return res['text']


@router.get("/d/latex/{dochash}", response_class=PlainTextResponse, tags=["access"])
async def view_pdf_hash(
        request: Request,
        dochash: str,
        db=Depends(get_db),
        t: str = ''):

    sql = """
    SELECT id_internal, ecli, text, appeal, meta->'labels' AS labels, views_hash, status
    FROM ecli_document
    WHERE hash = $1
    """

    res = await db.fetchrow(sql, dochash)
    if not res:
        raise HTTPException(status_code=404, detail="Document not found")
    else:
        await check_access(t, res['status'], db, dochash, res['views_hash'])

    return md2latex({
        'body': res['text'],
        'title': res['ecli'],
    })
