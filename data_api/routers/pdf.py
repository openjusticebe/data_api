from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from ..deps import (
    get_db,
    logger,
    doc_hash,
    templates,
)
from starlette.requests import Request

router = APIRouter()

# ############## ROUTE
# ####################


@router.get("/d/pdf/{dochash}", tags=["access"])
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
    doc = pandoc.read(res['text'])


@router.get("/pdf/{ecli}", tags=["access"])
async def view_pdf_hash(
        request: Request,
        ecli: str,
        db=Depends(get_db),
        t: str = ''):

    sql = """
    SELECT id_internal, ecli, text, appeal, meta->'labels' AS labels, views_hash, status
    FROM ecli_document
    WHERE ecli = $1
    AND status = 'public'
    """

    res = await db.fetchrow(sql, ecli)

    if not res:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = pandoc.read(res['text'])
