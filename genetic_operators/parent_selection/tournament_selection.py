import numpy as np

from basic_genetic import rng
from genetic_operators.parent_selection import BaseParentSelection


class TournamentParentSelection(BaseParentSelection):
    rng = np.random.default_rng()

    def select(self, costs, count):
        chosen = [rng.choice(len(costs), size=(2, 2), replace=False) for _ in range(count)]

        winners = []

        for i in range(count):

            parents = [0] * 2

            for p in range(2):
                chosen_costs = costs[chosen[i][p]]
                chosen_index = np.lexsort((chosen_costs[:, 1], chosen_costs[:, 0]))[0]
                parents[p] = chosen[i][p][chosen_index]

            winners.append(parents)

        return winners
