from fastapi import APIRouter

tags_metadata = [
    {
        "name": "collections",
        "description": "Operations on collections, depending authentified user"
    }
]

router = APIRouter(openapi_tags=tags_metadata)


@router.get("/c/", tags=["collections"])
async def read_collections():
    return []


@router.get("/c/{collection}", tags=["collections"])
async def read_collection(collection: str):
    return {
        "collection": collection
    }
