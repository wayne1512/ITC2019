import numpy as np

from util import random_gene

mutation_chance = 0.001


def select_parents_best2(genes, costs):
    combined = list(zip(genes, costs))

    combined.sort(key=lambda x: x[1])

    return [combined[0][0], combined[1][0]]


rng = np.random.default_rng()


def select_parents_roulette_wheel(genes, costs):
    weights = [1 / (cost[0] * cost[0]) if cost[0] > 0 else 999999999 for cost in costs]

    probabilities = np.array(weights) / np.sum(weights)

    chosen = rng.choice(genes, size=2, p=probabilities)

    return chosen


def crossover_uniform(gene1, gene2):
    choice = np.random.rand(*gene1.shape) > 0.5

    stats = np.count_nonzero(choice)

    return np.where(choice, gene1, gene2), stats


def mutate_uniform(gene, max_gene):
    choice = np.random.rand(*gene.shape) < mutation_chance

    return np.where(choice, gene, random_gene(max_gene))


def generate_new_population_basic_genetic(population, costs, maximumGenes):
    parents = select_parents_best2(population, costs)
    population_and_stats = [crossover_uniform(parents[0], parents[1]) for _ in range(len(population) - 2)]
    population = [a[0] for a in population_and_stats]
    stats = [a[1] for a in population_and_stats]
    population = [mutate_uniform(gene, maximumGenes) for gene in population]
    population.append(parents[0])
    population.append(parents[1])

    return population


def generate_new_population_roulette_wheel(population, costs, maximumGenes):
    best_parents = select_parents_best2(population, costs)

    population_and_stats = [crossover_uniform(*select_parents_roulette_wheel(population, costs)) for _ in
                            range(len(population) - 2)]
    population = [a[0] for a in population_and_stats]
    stats = [a[1] for a in population_and_stats]
    population = [mutate_uniform(gene, maximumGenes) for gene in population]
    population.append(best_parents[0])
    population.append(best_parents[1])

    return population
