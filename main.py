from parseInput import parse_xml
from solutionSearch import SolutionSearch
from util import extract_class_list, get_gene_maximums

# genetic settings
no_of_generations = 5000

population_size = 640

if __name__ == "__main__":
    file_path = "D:\Downloads\\assignmentRedownload\instances\late\\tg-spr18.xml"
    problem = parse_xml(file_path)

    classes = extract_class_list(problem)
    classes.sort(key=lambda c: len(c.time_options) * max(len(c.room_options), 1))

    maximumGenes = get_gene_maximums(classes)

    population = None
    costs = None

    search = SolutionSearch(problem, classes)
    search.solve()

    # for generation in range(no_of_generations):
    #     if population is None:
    #         population = [random_gene(maximumGenes) for _ in range(population_size)]
    #     else:
    #         population = generate_new_population_roulette_wheel(population, costs, maximumGenes)
    #
    #     costs = [calculate_total_cost(problem, classes, gene) for gene in population]
    #
    #     x = np.arange(population_size)
    #     fig, ax1 = plt.subplots()
    #
    #     ax1.plot(x, [cost[0] for cost in costs], linewidth=2, label='hard', color='r')
    #
    #     ax2 = ax1.twinx()
    #
    #     ax2.plot(x, [cost[1] for cost in costs], linewidth=2, label='soft', color='b')
    #
    #     # Adding legends
    #     ax1.legend(loc='upper left')
    #     ax2.legend(loc='upper right')
    #
    #     plt.title("generation " + str(generation))
    #
    #     plt.show()

    # for generation in range(no_of_generations):
