__all__ = ["get_parent_selection_method", "BaseParentSelection", "Best2ParentSelection", "RouletteWheelParentSelection",
           "RandomParentSelection", "TournamentParentSelection"]

from genetic_operators.parent_selection.base_parent_selection import BaseParentSelection
from genetic_operators.parent_selection.best_2_parent_selection import Best2ParentSelection
from genetic_operators.parent_selection.random_parent_selection import RandomParentSelection
from genetic_operators.parent_selection.roulette_wheel_parent_selection import RouletteWheelParentSelection
from genetic_operators.parent_selection.tournament_selection import TournamentParentSelection

_name_dict = {
    "best2": lambda: Best2ParentSelection(),
    "roulette": lambda: RouletteWheelParentSelection(),
    "random": lambda: RandomParentSelection(),
    "tournament": lambda: TournamentParentSelection()
}


def get_parent_selection_method(name):
    return _name_dict.get(name)()
