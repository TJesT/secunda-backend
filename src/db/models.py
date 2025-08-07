from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import BIT, JSON
from geoalchemy2 import Geometry

from src.db.base import PostgresBase


class Organizations(PostgresBase):
    __tablename__ = "organizations"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(128))
    phone_numbers = Column(ARRAY(String(16)), nullable=False, insert_default=[])
    building_id = Column(Integer(), ForeignKey("buildings.id"))
    activity_tag = Column(String(128), ForeignKey("activities.tag"))


class Buildings(PostgresBase):
    __tablename__ = "buildings"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    # In real-world scenario should consider more GSM-like approach.
    address = Column(String(1024))
    geo_point = Column(Geometry("POINT"))


class Activities(PostgresBase):
    __tablename__ = "activities"

    tag = Column(String(128), nullable=False, unique=False, primary_key=True)
    bitmap = Column(BIT(1024), nullable=False, unique=False)
