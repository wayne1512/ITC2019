import numpy as np


class UniformCrossover:

    def __init__(self, ratio=0.001):
        self.ratio = ratio

    def crossover(self, gene1, gene2):
        choice = np.random.rand(*gene1.shape) < self.ratio

        stats = np.count_nonzero(choice)

        child = np.where(choice, gene1, gene2)

        return child, stats
