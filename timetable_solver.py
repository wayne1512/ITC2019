import os
import time

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from checkpoint_manager import CheckpointManager
from depth_first_search_solver import DepthFirstSearchSolver
from genetic_operators.crossover import UniformCrossover
from genetic_operators.misc.local_search import local_search
from genetic_operators.mutation.uniform_mutation import UniformMutation
from genetic_operators.parent_selection import get_parent_selection_method
from penalty_calc import calculate_total_cost
from solution_search import SolutionSearch
from util import get_gene_maximums, random_gene


class TimetableSolver:

    def __init__(self, problem,
                 no_of_generations=1000,
                 population_size=50,
                 first_population_method="random",
                 parent_selection="tournament",
                 mutation_chance=0.001,
                 crossover_ratio=0.1,
                 checkpoint_dir=None,
                 graphs_dir=None,
                 graphs_interval=100,
                 local_search=False):
        self.problem = problem
        self.no_of_generations = no_of_generations
        self.population_size = population_size
        self.first_population_method = first_population_method
        self.parent_selection = get_parent_selection_method(parent_selection)
        self.mutation_chance = mutation_chance
        self.crossover_ratio = crossover_ratio
        self.local_search = local_search

        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_manager = CheckpointManager(checkpoint_dir)

        self.population = None
        self.costs = None
        self.maximum_genes = get_gene_maximums(self.problem.classes)

        self.init_population_construction_times = []

        self.mutation = UniformMutation(mutation_chance)
        self.crossover = UniformCrossover(crossover_ratio)

        self.generation = 0
        self.total_time_elapsed = 0

        self.fitness_history = pd.DataFrame(columns=['generation', 'hard_cost', 'soft_cost', 'time'])

        self.graphs_interval = graphs_interval
        self.graphs_dir = graphs_dir
        os.mkdir(self.graphs_dir)

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

        self.start_time = time.time() - self.total_time_elapsed  # if we recovered from a checkpoint, we need to
        # consider the time elapsed before the checkpoint

        while self.generation < self.no_of_generations:
            if self.population is None:
                if not self.generate_first_population():
                    return
            else:
                self.generate_new_population()

            if self.generation % self.graphs_interval == 0 or self.generation == self.no_of_generations - 1:
                self.update_graphs()

            self.generation += 1
            self.total_time_elapsed = time.time() - self.start_time
            self.checkpoint_manager.save_solver(self)

        self.update_graphs()

    def update_graphs(self):
        if self.generation > 0:
            x = np.arange(self.population_size)
            self.line1.set_data(x, [cost[0] for cost in self.costs])
            self.line2.set_data(x, [cost[1] for cost in self.costs])

            # Update the limits
            self.ax.set_xlim(0, max(x))
            self.ax.set_ylim(0, max([cost[0] for cost in self.costs]))

            # Redraw the figure
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.fig.savefig(f'{self.graphs_dir}/history.png')
            plt.pause(0.01)

            # Update the fitness plot
            self.fitness_line1.set_data(self.fitness_history['generation'], self.fitness_history['hard_cost'])
            self.fitness_line2.set_data(self.fitness_history['generation'], self.fitness_history['soft_cost'])
            self.fitness_fig.savefig(f'{self.graphs_dir}/fitness_plot.png')

            # Update the limits
            self.fitness_ax_hard.set_xlim(0, max(self.fitness_history['generation']))
            self.fitness_ax_hard.set_ylim(0, max(self.fitness_history['hard_cost']))
            self.fitness_ax_soft.set_xlim(0, max(self.fitness_history['generation']))
            self.fitness_ax_soft.set_ylim(0, max(self.fitness_history['soft_cost']))

            # Redraw the fitness figure
            self.fitness_fig.canvas.draw()
            self.fitness_fig.canvas.flush_events()
            plt.pause(0.01)

    def generate_first_population(self):
        if self.first_population_method == "random":
            self.population = [random_gene(self.maximum_genes) for _ in range(self.population_size)]
        elif self.first_population_method == "dfs":

            genes = []
            times = []

            max_attempts_before_first_success = 2
            max_attempts = 200
            failed_attempts = 0

            while len(genes) < self.population_size and failed_attempts < max_attempts:

                if len(genes) == 0 and failed_attempts == max_attempts_before_first_success:
                    break

                start_time = time.time()
                search = SolutionSearch(self.problem)
                solver = DepthFirstSearchSolver(search)
                solution = solver.solve(max_backtracks=2000, randomize_option=True)
                end_time = time.time()

                if solution['success']:
                    genes.append(search.get_result_as_gene())
                else:
                    failed_attempts += 1

                times.append((end_time - start_time, solution['success']))

            self.population = genes
            self.init_population_construction_times = times

            if len(genes) < self.population_size:
                print(f"Failed to generate enough genes for the initial population. "
                      f"Generated {len(genes)} genes out of {self.population_size} required.")
                return False

        self.costs = [calculate_total_cost(self.problem, gene) for gene in self.population]
        return True

    def generate_new_population(self):

        selected_parents_indices = self.parent_selection.select(np.array(self.costs), 1)[0]

        child = self.crossover.crossover(
            self.population[selected_parents_indices[0]], self.population[selected_parents_indices[1]])[0]

        child = self.mutation.mutate(child, self.maximum_genes)

        if self.local_search is not None and self.local_search:
            child, cost_of_child = local_search(child, self.maximum_genes, self.problem,
                                                graph_dir=
                                                os.path.join(self.graphs_dir, f"local_search_{self.generation}"))
        cost_of_child = calculate_total_cost(self.problem, child)

        worst_cost_index = np.lexsort((np.array(self.costs)[:, 1], np.array(self.costs)[:, 0]))[-1]
        if self.costs[worst_cost_index] > cost_of_child:
            self.population[worst_cost_index] = child
            self.costs[worst_cost_index] = cost_of_child

        self.fitness_history = pd.concat([self.fitness_history,
                                          pd.DataFrame([[self.generation, cost_of_child[0], cost_of_child[1],
                                                         time.time() - self.start_time]],
                                                       columns=['generation', 'hard_cost', 'soft_cost', 'time'])])

    def get_best_solution(self):
        if self.costs is None:
            return None, None
        best_index = np.lexsort((np.array(self.costs)[:, 1], np.array(self.costs)[:, 0]))[0]
        return self.population[best_index], self.costs[best_index]
