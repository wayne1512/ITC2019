import numpy as np

from basic_genetic import rng
from genetic_operators.parent_selection import BaseParentSelection

cost_of_hard_constraint = 1000000


class RouletteWheelParentSelection(BaseParentSelection):
    rng = np.random.default_rng()

    def select(self, costs, count):
        normalized_costs = costs[:, 0] * cost_of_hard_constraint + costs[:, 1]
        probabilities = normalized_costs / np.sum(normalized_costs, dtype=np.int64)
        chosen = [rng.choice(len(costs), size=2, p=probabilities, replace=False) for _ in range(count)]
        return chosen
