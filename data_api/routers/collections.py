from fastapi import APIRouter

router = APIRouter()


@router.get("/c/", tags=["collections"])
async def read_collections():
    return []


@router.get("/c/{collection}", tags=["collections"])
async def read_collection(collection: str):
    """
    Collection endpoint
    /c/[collection] lists members of a specific collection, curated by a group of moderators

    Some collections have a specific meaning, and are protected:
    /c/admin -> list everything
    /c/review -> latests documents awaiting review
    ...
    """
    return {
        "collection": collection
    }
