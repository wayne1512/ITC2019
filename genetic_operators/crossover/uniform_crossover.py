import numpy as np


class UniformCrossover:

    def __init__(self, ratio=0.001):
        self.ratio = ratio

    def crossover(self, gene1, gene2, problem=None):
        choice = np.random.rand(*gene1.shape) < self.ratio

        stats = np.count_nonzero(choice)

        child = np.where(choice, gene1, gene2)

        if problem is not None:
            for i, c in enumerate(problem.classes):
                if c.closed_room_time_combinations is not None and \
                        c.closed_room_time_combinations[child[i, 0], child[i, 1]]:
                    # if the chosen room time combination is closed,
                    # choose the room time combinations from one of the parents
                    child[i] = gene1[i] if np.random.random() > 0.5 else gene2[i]

        return child, stats
