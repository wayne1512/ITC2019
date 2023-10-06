import numpy as np

from util import random_gene

mutation_chance = 0.1


def select_parents(genes, costs):  # todo improve greatly
    combined = list(zip(genes, costs))

    combined.sort(key=lambda x: x[1])

    return [combined[0], combined[1]]


def crossover(gene1, gene2):
    choice = np.random.rand(*gene1.shape) > 0.5

    stats = np.count_nonzero(choice)

    return np.where(choice, gene1, gene2), stats


def mutate(gene, max_gene):
    choice = np.random.rand(*gene.shape) < mutation_chance

    stats = np.count_nonzero(choice)

    return np.where(choice, gene, random_gene(max_gene))


def generate_new_population_basic_genetic(population, costs, maximumGenes):
    parents = select_parents(population, costs)
    population_and_stats = [crossover(parents[0][0], parents[1][0]) for _ in range(len(population) - 2)]
    population = [a[0] for a in population_and_stats]
    stats = [a[1] for a in population_and_stats]
    population = [mutate(gene, maximumGenes) for gene in population]
    population.append(parents[0][0])
    population.append(parents[1][0])

    return population
