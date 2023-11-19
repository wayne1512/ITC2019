import numpy as np
from matplotlib import pyplot as plt

from basic_genetic import generate_new_population_roulette_wheel
from penalty_calc import calculate_total_cost
from util import get_gene_maximums, random_gene


def run(problem, no_of_generations=1000, population_size=64):
    population = None
    costs = None
    maximum_genes = get_gene_maximums(problem.classes)
    for generation in range(no_of_generations):
        if population is None:
            population = [random_gene(maximum_genes) for _ in range(population_size)]
        else:
            population = generate_new_population_roulette_wheel(population, costs, maximum_genes)

        costs = [calculate_total_cost(problem, gene) for gene in population]

        x = np.arange(population_size)
        fig, ax1 = plt.subplots()

        ax1.plot(x, [cost[0] for cost in costs], linewidth=2, label='hard', color='r')

        ax2 = ax1.twinx()

        ax2.plot(x, [cost[1] for cost in costs], linewidth=2, label='soft', color='b')

        # Adding legends
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        plt.title("generation " + str(generation))

        plt.show()
