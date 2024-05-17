import numpy as np


class MoveMutation:

    def __init__(self, chance=0.001):
        self.chance = chance

    def mutate(self, gene, max_gene):
        row = np.random.randint(0, len(gene))

        if max_gene[row, 0] >= 0:
            gene[row, 0] = np.random.randint(0, max_gene[row, 0] + 1)
        if max_gene[row, 1] >= 0:
            gene[row, 1] = np.random.randint(0, max_gene[row, 1] + 1)

        return gene
