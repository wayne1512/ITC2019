import numpy as np
from matplotlib import pyplot as plt

from basic_genetic import generate_new_population_roulette_wheel
from costCalcuation.distributions.create_distribtion_helper import create_helper_for_distribution
from parse_input import parse_xml
from penalty_calc import calculate_total_cost
from util import random_gene, get_gene_maximums

# genetic settings
no_of_generations = 10

population_size = 10

if __name__ == "__main__":

    debug_read_checkpoint = False

    # file_path = "input.xml"
    # file_path = "D:\\Downloads\\assignmentRedownload\\instances\\early\\agh-ggis-spr17.xml"
    file_path = "D:\\Downloads\\assignmentRedownload\\instances\\middle\\muni-fi-spr17.xml"
    # file_path = "D:\\Downloads\\assignmentRedownload\\instances\\late\\muni-pdfx-fal17.xml"

    problem = parse_xml(file_path)

    for d in problem.distributions:
        d.distribution_helper = create_helper_for_distribution(problem, d)

    # if debug_read_checkpoint:
    #     gene = np.load("checkpoint.npy")
    # else:
    #     search = SolutionSearch(problem)
    #     solver = InitialTimetableTreeSearchSolver(search)
    #     solver.solve()
    #     gene = search.get_result_as_gene()
    #
    #     np.save("checkpoint", gene)

    # print(calculate_total_cost(problem, gene))
    # generate_xml(problem, gene)

    population = None
    costs = None

    maximumGenes = get_gene_maximums(problem.classes)

    for generation in range(no_of_generations):
        if population is None:
            population = [random_gene(maximumGenes) for _ in range(population_size)]
        else:
            population = generate_new_population_roulette_wheel(population, costs, maximumGenes)

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
