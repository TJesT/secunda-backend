from typing import Literal, Sequence, TypedDict, Unpack
from sqlalchemy import cast, text, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import BIT, insert
from geoalchemy2.functions import ST_DWithin


from src.db.models import Organizations, Activities, Buildings
from src.cruds.base import MAX_LIMIT


SQL_FIND_BY_POINT_AND_RADIUS = """select o.id, o."name", o.phone_numbers, b.address, b.geo_point, o.activity
from organizations o 
left join buildings b on o.building_id = b.id
where ST_DWithin('POINT({lon} {lat})'::geography, buildings.geo_point, {r})
limit {limit}
offset {offset}
"""


class OrganizationsFields(TypedDict, total=False):
    id: int
    name: str
    phone_numbers: list[str]
    building_id: int
    activity_tag: str


class OrganizationsCRUD:
    @staticmethod
    async def is_empty(
        session: AsyncSession,
    ) -> bool:
        return (
            None
            is (
                await session.execute(
                    select(Organizations).limit(1),
                )
            ).one_or_none()
        )

    @staticmethod
    async def insert(
        session: AsyncSession,
        values: Sequence[OrganizationsFields | tuple[str, list[str], int, str]],
    ):
        await session.execute(insert(Organizations).values(values))
        await session.commit()

    @staticmethod
    async def read(
        session: AsyncSession,
        limit: int = MAX_LIMIT,
        offset: int = 0,
        **filter: Unpack[OrganizationsFields],
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
                .where(ST_DWithin(f"POINT({lon} {lat})", Buildings.geo_point, r))
                .limit(limit)
                .offset(offset)
            )
        ).fetchall()
        # return (await session.execute(text(sql))).fetchall()

    @staticmethod
    async def find_by_activity(
        session: AsyncSession,
        tag: str,
        bits: int,
        action: Literal["exact", "includes"],
        *,
        limit: int = MAX_LIMIT,
        offset: int = 0,
    ):

        casted_bits = cast(bits.to_bytes(), BIT(1024))
        casted_zero = cast(int(0).to_bytes(), BIT(1024))
        bits_clause = {
            "exact": Activities.tag == tag,
            "includes": (
                (Activities.bitmap.bitwise_and(casted_bits) > casted_zero)
                & (Activities.bitmap <= casted_bits)
            ),
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
