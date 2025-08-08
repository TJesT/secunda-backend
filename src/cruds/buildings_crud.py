from typing import Sequence, TypedDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.db.models import Buildings


class BuildingsFields(TypedDict):
    address: str
    geo_point: tuple[float, float]


class BuildingsCRUD:
    @staticmethod
    async def is_empty(
        session: AsyncSession,
    ) -> bool:
        return (
            None
            is (
                await session.execute(
                    select(Buildings).limit(1),
                )
            ).one_or_none()
        )

    @staticmethod
    async def insert(
        session: AsyncSession,
        values: Sequence[BuildingsFields | tuple[str, tuple[float, float]]],
    ):
        await session.execute(insert(Buildings).values(values))
        await session.commit()


buildings_crud = BuildingsCRUD()
