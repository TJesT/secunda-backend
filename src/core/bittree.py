from pydantic import BaseModel, model_validator
from functools import reduce
from src.config import tree_settings


class Tree(BaseModel):
    tag: str
    children: list["Tree"]

    @model_validator(mode="before")
    @classmethod
    def check_max_height(cls, values: dict):
        def check_depth(tree_dict: dict, current=1):
            if current > tree_settings.max_height:
                raise ValueError(
                    "Tree depth exceeds maximum allowed"
                    f"height of {tree_settings.max_height}"
                )

            children = tree_dict.get("children", [])
            for child in children:
                check_depth(child, current + 1)

        check_depth(values)

        return values


type Forest = Tree | list[Tree]


class TreeBuilder:
    def __init__(self):
        self.bitmaps = {}

    def build_bitmaps(
        self,
        tree: Forest,
        /,
        return_carry: bool = False,
        autocache: bool = True,
    ) -> dict[str, int] | tuple[dict[str, int], bool]:

        carry: int = -1

        def _build_bitmaps(tree: list[Tree] | Tree) -> dict[str, int]:
            nonlocal carry

            match tree:
                case node_list if isinstance(node_list, list):
                    return reduce(
                        dict.__or__,
                        (_build_bitmaps(child) for child in node_list),
                        {},
                    )

                case Tree(tag=tag, children=children) if children == []:
                    return {tag: 0b1 << (carry := carry + 1)}

                case Tree(tag=tag, children=children):
                    children_bitmap = _build_bitmaps(children)
                    parent_bitmap = {
                        tag: reduce(int.__or__, children_bitmap.values(), 0b0)
                    }
                    return children_bitmap | parent_bitmap

                case _:
                    return {}

        bitmaps = _build_bitmaps(tree)
        if autocache:
            self.bitmaps = bitmaps

        if return_carry:
            return bitmaps, carry + 1

        return bitmaps

    def tree2bits(
        self,
        tree: Forest,
        /,
        bitmaps: dict[str, int] = None,
    ) -> int:
        if bitmaps is None:
            bitmaps = self.bitmaps

        def _get_leafs(tree: Forest) -> list[str]:
            match tree:
                case node_list if isinstance(node_list, list):
                    return reduce(list.__add__, map(_get_leafs, node_list), [])

                case Tree(tag, children) if children == []:
                    return [tag]

                case Tree(tag, children):
                    return _get_leafs(children)

                case _:
                    return []

        leafs = _get_leafs(tree)
        bits = reduce(int.__ror__, map(bitmaps.get, leafs), 0)

        return bits


tree_builder = TreeBuilder()
