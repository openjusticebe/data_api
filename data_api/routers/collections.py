from fastapi import APIRouter, Depends, HTTPException, status
from ..models import (
    User,
)
from ..auth import (
    get_current_active_user_opt,
)
from ..deps import (
    # config,
    get_db,
    logger,
)

router = APIRouter()
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
bad_request = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Bad Request"
)
# ################################ COLLECTIONS
# ############################################


class Collections:
    NEW = 'new'

    @staticmethod
    async def review(user, db):
        if not user.admin:
            raise credentials_exception
        record = await Collections._by_status(Collections.NEW, db)
        return record

    @staticmethod
    async def _by_status(state, db):
        sql = """
        SELECT id_internal as id, ecli, status, appeal, meta, lang, date_created, date_updated
        FROM ecli_document
        WHERE status = $1
        """
        res = await db.fetch(sql, state)
        return [dict(r) for r in res]



# ##################################### ROUTES
# ############################################
@router.get("/c/", tags=["collections"])
async def read_collections(current_user: User = Depends(get_current_active_user_opt)):
    return []


@router.get("/c/{collection}", tags=["collections"])
async def read_collection(
        collection: str,
        current_user: User = Depends(get_current_active_user_opt),
        db=Depends(get_db)):
    """
    Collection endpoint
    /c/[collection] lists contents of a specific collection, curated by a group of moderators

    Some collections have a specific meaning, and are protected:
    /c/admin -> list everything
    /c/review -> latests documents awaiting review
    ...
    """
    logger.debug('User %s queried collection %s', current_user, collection)
    try:
        call = getattr(Collections, collection)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection does not exist"
        )
    data = await call(current_user, db)
    return data
