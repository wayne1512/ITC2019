import numpy as np
from matplotlib import pyplot as plt

from checkpoint_manager import CheckpointManager
from genetic_operators.crossover import UniformCrossover
from genetic_operators.misc.local_search import local_search
from genetic_operators.mutation.uniform_mutation import UniformMutation
from genetic_operators.parent_selection import RandomParentSelection
from penalty_calc import calculate_total_cost
from util import get_gene_maximums, random_gene


class TimetableSolver:

    def __init__(self, problem,
                 solid_state=False,
                 no_of_generations=1000,
                 population_size=64,
                 parent_selection=RandomParentSelection(),
                 mutation_chance=0.001,
                 crossover_ratio=0.1,
                 checkpoint_dir=None):
        self.solid_state = solid_state
        self.problem = problem
        self.no_of_generations = no_of_generations
        self.population_size = population_size
        self.parent_selection = parent_selection
        self.mutation_chance = mutation_chance
        self.crossover_ratio = crossover_ratio

        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_manager = CheckpointManager(checkpoint_dir)

        self.population = None
        self.costs = None
        self.maximum_genes = get_gene_maximums(self.problem.classes)

        self.mutation = UniformMutation(mutation_chance)
        self.crossover = UniformCrossover(crossover_ratio)

        self.generation = 0

    def run(self):
        while self.generation < self.no_of_generations:
            if self.population is None:
                self.population = [random_gene(self.maximum_genes, self.problem) for _ in range(self.population_size)]
                self.costs = [calculate_total_cost(self.problem, gene) for gene in self.population]
            else:
                self.generate_new_population()

            if self.generation % 1 == 0 or self.generation == self.no_of_generations - 1:
                x = np.arange(self.population_size)
                fig, ax1 = plt.subplots()

                ax1.plot(x, [cost[0] for cost in self.costs], linewidth=2, label='hard', color='r')

                ax2 = ax1.twinx()

                ax2.plot(x, [cost[1] for cost in self.costs], linewidth=2, label='soft', color='b')

                # Adding legends
                ax1.legend(loc='upper left')
                ax2.legend(loc='upper right')

                plt.title("generation " + str(self.generation))

                plt.show()

            self.generation += 1
            self.checkpoint_manager.save_solver(self)

    def generate_new_population(self):

        if not self.solid_state:

            selected_parents_indices = self.parent_selection.select(np.array(self.costs), self.population_size)

            self.population = [self.crossover.crossover(self.population[p1], self.population[p2], self.problem)[0] for
                               (p1, p2) in
                               selected_parents_indices]

            self.population = [self.mutation.mutate(gene, self.maximum_genes, self.problem) for gene in self.population]

            self.costs = [calculate_total_cost(self.problem, gene) for gene in self.population]
        else:
            selected_parents_indices = self.parent_selection.select(np.array(self.costs), 1)[0]

            child = self.crossover.crossover(
                self.population[selected_parents_indices[0]], self.population[selected_parents_indices[1]],
                self.problem)[0]

            child = self.mutation.mutate(child, self.maximum_genes, self.problem)

            child, cost_of_child = local_search(child, self.maximum_genes, self.problem)
            # cost_of_child = calculate_total_cost(self.problem, child)

            worst_cost_index = np.lexsort((np.array(self.costs)[:, 1], np.array(self.costs)[:, 0]))[-1]
            if self.costs[worst_cost_index] > cost_of_child:
                self.population[worst_cost_index] = child
                self.costs[worst_cost_index] = cost_of_child
