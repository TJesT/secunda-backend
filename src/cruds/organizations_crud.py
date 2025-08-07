from sqlalchemy import cast, text, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import BIT
from typing import Literal, TypedDict, Unpack

from src.db.models import Organizations, Activities, Buildings


SQL_FIND_BY_POINT_AND_RADIUS = """select o.id, o."name", o.phone_numbers, b.addres, b.geo_point, o.activity
from organizations o 
left join buildings b on o.building_id = b.id
where ST_DWithin('POINT({lon} {lat})'::geography, buildings.geo_point, {r})
limit {limit}
offset {offset}
"""

MAX_LIMIT = 999_999_999_999_999


class ReadFilter(TypedDict, total=False):
    id: int
    name: str
    building_id: int
    activity_tag: str


class OrganizationsCRUD:
    @staticmethod
    async def read(
        session: AsyncSession,
        limit: int = MAX_LIMIT,
        offset: int = 0,
        **filter: Unpack[ReadFilter],
    ):
        return (
            await session.execute(
                select(
                    Organizations.id,
                    Organizations.name,
                    Organizations.phone_numbers,
                    Organizations.building_id,
                    Buildings.address,
                    Buildings.geo_point,
                    Organizations.activity_tag,
                )
                .join(
                    Buildings,
                    onclause=Organizations.building_id == Buildings.id,
                )
                .where(
                    and_(
                        *[
                            getattr(Organizations, field) == value
                            for field, value in filter.items()
                        ]
                    )
                )
                .limit(limit)
                .offset(offset)
            )
        ).fetchall()

    @staticmethod
    async def find_by_radius(
        session: AsyncSession,
        lon: float,
        lat: float,
        r: float,
        *,
        limit: int = MAX_LIMIT,
        offset: int = 0,
    ):
        sql = SQL_FIND_BY_POINT_AND_RADIUS.format(
            lon=lon,
            lat=lat,
            r=r,
            limit=limit,
            offset=offset,
        )
        return (await session.execute(text(sql))).fetchall()

    @staticmethod
    async def find_by_activity(
        session: AsyncSession,
        bits: int,
        action: Literal["exact", "includes"],
        *,
        limit: int = MAX_LIMIT,
        offset: int = 0,
    ):

        casted_bits = cast(bits.to_bytes(), BIT(1024))
        bits_clause = {
            "exact": Activities.bitmap.bitwise_and(casted_bits) == casted_bits,
            "includes": Activities.bitmap.bitwise_and(casted_bits)
            >= cast(int().to_bytes(), BIT(1024)),
        }
        return (
            await session.execute(
                select(
                    Organizations.id,
                    Organizations.name,
                    Organizations.phone_numbers,
                    Organizations.building_id,
                    Buildings.address,
                    Buildings.geo_point,
                    Organizations.activity_tag,
                )
                .join(
                    Buildings,
                    onclause=Organizations.building_id == Buildings.id,
                )
                .join(
                    Activities,
                    onclause=Organizations.activity_tag == Activities.tag,
                )
                .where(bits_clause[action])
                .limit(limit)
                .offset(offset)
            )
        ).fetchall()


organizations_crud = OrganizationsCRUD()
