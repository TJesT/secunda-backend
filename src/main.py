import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from src.api import routers
from src.cruds import activities_crud
from src.core.bittree import tree_builder, Tree
from src.config import tree_settings


async def create_tags_if_not_exist():
    if not await activities_crud.read():
        if not tree_settings.struct:
            raise RuntimeError(
                "Database does not contain tags. You should set env TREE_STRUCT."
            )
        activity_tags = tree_builder.build_bitmaps(tree_settings.struct)
        await activities_crud.update(activity_tags)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await create_tags_if_not_exist()
    tree = tree_settings.struct
    tree = tree if isinstance(tree, list) else [tree]
    tree_builder.build_bitmaps(list(map(Tree.model_validate, tree)))
    yield


app = FastAPI(lifespan=lifespan)


for router in routers:
    app.include_router(router)


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="SECUNDA-API docs")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
