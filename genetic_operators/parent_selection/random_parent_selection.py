import numpy as np

from basic_genetic import rng
from genetic_operators.parent_selection import BaseParentSelection


class RandomParentSelection(BaseParentSelection):
    rng = np.random.default_rng()

    def select(self, costs, count):
        chosen = [rng.choice(len(costs), size=2, replace=False) for _ in range(count)]
        return chosen
