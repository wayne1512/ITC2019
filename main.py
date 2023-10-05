import matplotlib.pyplot as plt
import numpy as np

from parseInput import parse_xml
from penaltyCalc import calculate_total_cost
from util import extract_class_list, random_gene, get_gene_maximums

# genetic settings
no_of_generations = 5000

population_size = 64

mutation_chance = 0.9


if __name__ == "__main__":
    file_path = "input.xml"
    problem = parse_xml(file_path)

    classes = extract_class_list(problem)

    maximumGenes = get_gene_maximums(classes)

    population = [random_gene(problem, maximumGenes) for _ in range(population_size)]

    # save_file = "output/"+datetime.today().strftime('%Y-%m-%d %H:%M:%S')+"/"

    costs = [calculate_total_cost(problem, classes, gene) for gene in population]

    x = np.arange(population_size)
    fig, ax1 = plt.subplots()

    ax1.plot(x, [cost[0] for cost in costs], linewidth=2, label='hard', color='r')

    ax2 = ax1.twinx()

    ax2.plot(x, [cost[1] for cost in costs], linewidth=2, label='soft', color='b')

    # Adding legends
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.title("soft and hard")

    plt.show()

    # for generation in range(no_of_generations):
