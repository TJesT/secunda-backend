import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html

from src.config import app_settings
from src.api import routers
from src.data.factories import (
    insert_activities_if_not_exist,
    insert_buildings_if_not_exist,
    insert_organizations_if_not_exist,
)
from src.cruds import activities_crud
from src.core.bittree import tree_builder
from src.db.base import async_session_factory


async def pull_activities():
    async with async_session_factory() as session:
        result = await activities_crud.read(session)

        return {row[0].tag: int.from_bytes(row[0].bitmap.bytes[::-1]) for row in result}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await insert_activities_if_not_exist()
    tree_builder.bitmaps = await pull_activities()
    await insert_buildings_if_not_exist()
    await insert_organizations_if_not_exist()
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
