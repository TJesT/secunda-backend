from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import AfterValidator, BaseModel, field_validator
from shapely import wkb
from geoalchemy2 import WKBElement

from src.config import LAT2METRES_COEFF
from src.db import get_db_session
from src.cruds import organizations_crud, MAX_LIMIT
from src.core.bittree import tree_builder


router = APIRouter(prefix="/organizations")


def validate_activity(activity: str) -> str:
    if activity not in tree_builder.bitmaps:
        raise ValueError(f"Invalid activity `{activity}`")

    return activity


def validate_metres2degrees(metres: float):
    return metres * LAT2METRES_COEFF


type Activity = Annotated[str, AfterValidator(validate_activity)]
type MetresInDegrees = Annotated[float, AfterValidator(validate_metres2degrees)]


class OrganizationResponse(BaseModel):
    id: int
    name: str
    phone_numbers: list[str]
    building_id: int
    address: str
    geo_point: tuple[float, float]
    activity_tag: str

    @field_validator("geo_point", mode="before")
    @classmethod
    def convert_geo_point_from_wkb(cls, raw):
        if isinstance(raw, WKBElement):
            point = wkb.loads(raw.data)
            return (point.x, point.y)

        return raw


@router.get("/by-id/{organization_id}", status_code=status.HTTP_200_OK)
async def get_org_by_id(
    organization_id: int,
    *,
    session=Depends(get_db_session),
) -> OrganizationResponse:
    result = await organizations_crud.read(session, id=organization_id, limit=1)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Organization not found.",
        )

    return result[0]


@router.get("/by-name/{name}", status_code=status.HTTP_200_OK)
async def get_org_by_name(
    name: str,
    *,
    session=Depends(get_db_session),
) -> OrganizationResponse:
    # Trigramm search might be used to get aproximate results
    result = await organizations_crud.read(session, name=name, limit=1)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Organization not found.",
        )

    return result[0]


@router.get("/by-building/{building_id}", status_code=status.HTTP_200_OK)
async def get_org_by_building(
    building_id: int,
    limit: int = MAX_LIMIT,
    offset: int = 0,
    *,
    session=Depends(get_db_session),
) -> list[OrganizationResponse]:
    result = await organizations_crud.read(
        session,
        building_id=building_id,
        limit=limit,
        offset=offset,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Organization not found.",
        )

    return result


@router.get("/by-activity/{activity}", status_code=status.HTTP_200_OK)
async def get_orgs_by_exact_activity(
    activity: Activity,
    limit: int = MAX_LIMIT,
    offset: int = 0,
    *,
    session=Depends(get_db_session),
) -> list[OrganizationResponse]:
    bits = tree_builder.bitmaps[activity]

    result = await organizations_crud.find_by_activity(
        session,
        tag=activity,
        bits=bits,
        action="exact",
        limit=limit,
        offset=offset,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Organization not found.",
        )

    return result


@router.get("/by-activity-with-children/{activity}", status_code=status.HTTP_200_OK)
async def get_orgs_including_activity(
    activity: Activity,
    limit: int = MAX_LIMIT,
    offset: int = 0,
    *,
    session=Depends(get_db_session),
) -> list[OrganizationResponse]:
    bits = tree_builder.bitmaps[activity]

    result = await organizations_crud.find_by_activity(
        session,
        tag=activity,
        bits=bits,
        action="includes",
        limit=limit,
        offset=offset,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Organization not found.",
        )

    return result


@router.get("/by-point-and-radius", status_code=status.HTTP_200_OK)
async def get_orgs_by_exact_activity(
    longitude: float,
    latitude: float,
    radius_in_meters: MetresInDegrees,
    limit: int = MAX_LIMIT,
    offset: int = 0,
    *,
    session=Depends(get_db_session),
) -> list[OrganizationResponse]:
    result = await organizations_crud.find_by_radius(
        session,
        lon=longitude,
        lat=latitude,
        r=radius_in_meters,
        limit=limit,
        offset=offset,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Organization not found.",
        )

    return result
