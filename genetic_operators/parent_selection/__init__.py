__all__ = ["get_parent_selection_method", "BaseParentSelection", "Best2ParentSelection", "RouletteWheelParentSelection",
           "RandomParentSelection"]

from genetic_operators.parent_selection.base_parent_selection import BaseParentSelection
from genetic_operators.parent_selection.best_2_parent_selection import Best2ParentSelection
from genetic_operators.parent_selection.random_parent_selection import RandomParentSelection
from genetic_operators.parent_selection.roulette_wheel_parent_selection import RouletteWheelParentSelection

_name_dict = {
    "best2": lambda: Best2ParentSelection(),
    "roulette": lambda: RouletteWheelParentSelection(),
    "random": lambda: RandomParentSelection()
}


def get_parent_selection_method(name):
    return _name_dict.get(name)()
