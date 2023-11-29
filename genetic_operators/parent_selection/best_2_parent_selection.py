import numpy as np

from genetic_operators.parent_selection import BaseParentSelection


class Best2ParentSelection(BaseParentSelection):
    def select(self, costs, count):
        sorted_indices = np.lexsort((costs[:, 1], costs[:, 0]))
        top_indices = sorted_indices[-2:]
        return np.tile(top_indices, (count, 1))
