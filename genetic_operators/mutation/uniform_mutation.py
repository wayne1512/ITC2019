import numpy as np

from util import random_gene


class UniformMutation:

    def __init__(self, chance=0.001):
        self.chance = chance

    def mutate(self, gene, max_gene, problem):
        choice = np.random.rand(*gene.shape) < self.chance
        return np.where(choice, random_gene(max_gene, problem), gene)
