from typing import Sequence, TypedDict, Unpack
from dataclasses import dataclass
from asyncpg import BitString
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.db.models import Activities
from src.cruds.base import MAX_LIMIT


@dataclass
class ActivityRow:
    tag: str
    bitmap: BitString


class ActivitiesFields(TypedDict, total=False):
    tag: str
    bitmap: bytes


class ActivitiesCRUD:
    @staticmethod
    async def is_empty(
        session: AsyncSession,
    ) -> bool:
        return (
            None
            is (
                await session.execute(
                    select(Activities).limit(1),
                )
            ).one_or_none()
        )

    @staticmethod
    async def read(
        session: AsyncSession,
        *,
        limit: int = MAX_LIMIT,
        offset: int = 0,
        **filters: Unpack[ActivitiesFields],
    ) -> Sequence[tuple[ActivityRow]]:
        return (
            await session.execute(
                select(Activities)
                .where(
                    and_(
                        *[
                            getattr(Activities, field) == value
                            for field, value in filters.items()
                        ]
                    )
                )
                .limit(limit)
                .offset(offset)
            )
        ).fetchall()

    @staticmethod
    async def insert(
        session: AsyncSession,
        values: Sequence[ActivitiesFields | tuple[str, bytes]],
    ):
        await session.execute(insert(Activities).values(values))
        await session.commit()


activities_crud = ActivitiesCRUD()
