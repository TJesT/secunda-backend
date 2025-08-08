"""
All factories should be rewritten with respect to BaseCRUD being a Parent to ALL CRUD's.
Then they can use wrappers, methods and nested functions to achieve TRUE factory style and no code repetition.
"""

from itertools import cycle
from src.config import LAT2METRES_COEFF, tree_settings
from src.db.base import async_session_factory
from src.core.bittree import tree_builder, Tree, Forest
from src.cruds import activities_crud, buildings_crud, organizations_crud

CONST_ADDRESSES = [
    "Блюхера, 32/1",
    "Блюхера, 32/2",
    "Коммунистическая, 1091",
    "Покрышкина, 14",
    "Пивоваров, 911",
    "Постакадемическая, 16к4",
    "Балабановская, 16",
    "Дробышевская, 91/4",
    "Лейбница, 56",
    "Карамзина, 77",
    "Столяров, 80к1",
    "Академическая, 16к4",
]
CONST_POINTS = [
    f"POINT(0.0 0.0)",
    f"POINT(0.0 {1.0 * LAT2METRES_COEFF})",
    f"POINT({1000.0 * LAT2METRES_COEFF} 0.0)",
    f"POINT(0.0 {500.0 * LAT2METRES_COEFF})",
    f"POINT({333.3 * LAT2METRES_COEFF} {333.3 * LAT2METRES_COEFF})",
    f"POINT({1000.0 * LAT2METRES_COEFF} {1000.0 * LAT2METRES_COEFF})",
    f"POINT(0.0 0.0)",
    f"POINT({1.0 * LAT2METRES_COEFF} 0.0)",
    f"POINT(0.0 {1000.0 * LAT2METRES_COEFF})",
    f"POINT({500.0 * LAT2METRES_COEFF} 0.0)",
    f"POINT({666.6 * LAT2METRES_COEFF} {666.6 * LAT2METRES_COEFF})",
    f"POINT({1500.0 * LAT2METRES_COEFF} 0.0)",
]
CONST_COMPANIES = [
    'ООО "Моя Оборона"',
    'ЗАО "Блачные цены"',
    'ОАО "Везение"',
    'ООО "Лучшая компания"',
    'ЗАО "Худший предприниматель"',
    'ОАО "Разадача"',
    'ООО "Стаканы на столах"',
    'ЗАО "Чёрное солнце"',
    'ОАО "Ели мясо мужики"',
    'ООО "Куда уходит детство"',
    'ЗАО "Мир"',
    'ОАО "Губанов"',
]
CONST_PHONES = [
    ["+7(911)111-11-11", "11-111-11"],
    ["+385 7777-77-77"],
    ["+91 222-11-22"],
    ["2-222-222", "88002222222"],
    ["333-33-33"],
    ["8-800-555-35-35"],
    ["112"],
    ["1-345-123-45-61"],
    ["+64 1234567"],
    ["11-175-479-23-76"],
    ["+79547341925"],
    ["4-444-444", "444-44-44", "88004444444"],
]


async def insert_activities_if_not_exist():
    async with async_session_factory() as session:
        if not await activities_crud.is_empty(session):
            return

    if not tree_settings.struct:
        raise RuntimeError(
            "Database does not contain activities. You should set env TREE_STRUCT."
        )

    tree = tree_settings.struct
    forest: Forest = tree if isinstance(tree, list) else [tree]
    forest: Forest = list(map(Tree.model_validate, forest))
    activity_tags = tree_builder.build_bitmaps(forest, autocache=True)
    values = list(map(lambda x: (x[0], x[1].to_bytes()), activity_tags.items()))

    async with async_session_factory() as session:
        await activities_crud.insert(session, values)
        await session.commit()


async def insert_buildings_if_not_exist():
    async with async_session_factory() as session:
        if not await buildings_crud.is_empty(session):
            return

    async with async_session_factory() as session:
        await buildings_crud.insert(
            session, list(zip(range(1, 13), CONST_ADDRESSES, CONST_POINTS))
        )
        await session.commit()


async def insert_organizations_if_not_exist():
    async with async_session_factory() as session:
        if not await organizations_crud.is_empty(session):
            return

    async with async_session_factory() as session:
        await organizations_crud.insert(
            session,
            [
                {
                    "id": _id,
                    "name": name,
                    "phone_numbers": phones,
                    "building_id": bid,
                    "activity_tag": atag,
                }
                for _id, name, phones, bid, atag in list(
                    zip(
                        range(1, 13),
                        CONST_COMPANIES,
                        CONST_PHONES,
                        range(12, 0, -1),
                        cycle(list(tree_builder.bitmaps.keys())),
                    )
                )
            ],
        )
