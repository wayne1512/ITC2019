import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from checkpoint_manager import CheckpointManager
from genetic_operators.crossover import UniformCrossover
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

        self.fitness_history = pd.DataFrame(columns=['generation', 'hard_cost', 'soft_cost'])

        # Initialize the figures and axes for the plots
        self.fig, self.ax = plt.subplots()
        self.line1, = self.ax.plot([], [], linewidth=2, label='hard', color='r')
        self.line2, = self.ax.plot([], [], linewidth=2, label='soft', color='b')
        self.ax.legend(loc='upper left')

        # Initialize the figures and axes for the fitness plot
        self.fitness_fig, self.fitness_ax_hard = plt.subplots()
        self.fitness_ax_soft = self.fitness_ax_hard.twinx()
        self.fitness_ax_hard.set_xlabel('generation')
        self.fitness_line1, = self.fitness_ax_hard.plot([], [], linewidth=2, label='hard', color='r')
        self.fitness_line2, = self.fitness_ax_soft.plot([], [], linewidth=2, label='soft', color='b')
        self.fitness_ax_hard.legend(loc='upper left')
        self.fitness_ax_soft.legend(loc='upper right')

    def run(self):
        while self.generation < self.no_of_generations:
            if self.population is None:
                self.population = [random_gene(self.maximum_genes, self.problem) for _ in range(self.population_size)]
                self.costs = [calculate_total_cost(self.problem, gene) for gene in self.population]
            else:
                self.generate_new_population()

            if self.generation % 1 == 0 or self.generation == self.no_of_generations - 1:
                x = np.arange(self.population_size)
                self.line1.set_data(x, [cost[0] for cost in self.costs])
                self.line2.set_data(x, [cost[1] for cost in self.costs])

                # Update the limits
                self.ax.set_xlim(0, max(x))
                self.ax.set_ylim(0, max([cost[0] for cost in self.costs]))

                # Redraw the figure
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                plt.pause(0.01)

                if self.generation > 0:
                    # Update the fitness plot
                    self.fitness_line1.set_data(self.fitness_history['generation'], self.fitness_history['hard_cost'])
                    self.fitness_line2.set_data(self.fitness_history['generation'], self.fitness_history['soft_cost'])

                    # Update the limits
                    self.fitness_ax_hard.set_xlim(0, max(self.fitness_history['generation']))
                    self.fitness_ax_hard.set_ylim(0, max(self.fitness_history['hard_cost']))
                    self.fitness_ax_soft.set_xlim(0, max(self.fitness_history['generation']))
                    self.fitness_ax_soft.set_ylim(0, max(self.fitness_history['soft_cost']))

                    # Redraw the fitness figure
                    self.fitness_fig.canvas.draw()
                    self.fitness_fig.canvas.flush_events()
                    plt.pause(0.01)

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

            # child, cost_of_child = local_search(child, self.maximum_genes, self.problem)
            cost_of_child = calculate_total_cost(self.problem, child)

            worst_cost_index = np.lexsort((np.array(self.costs)[:, 1], np.array(self.costs)[:, 0]))[-1]
            if self.costs[worst_cost_index] > cost_of_child:
                self.population[worst_cost_index] = child
                self.costs[worst_cost_index] = cost_of_child

            self.fitness_history = pd.concat([self.fitness_history,
                                              pd.DataFrame([[self.generation, cost_of_child[0], cost_of_child[1]]],
                                                           columns=['generation', 'hard_cost', 'soft_cost'])])
