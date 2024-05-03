import os
import time

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from genetic_operators.misc.local_search import local_search

matplotlib.use('agg')  # https://github.com/matplotlib/matplotlib/issues/20067#issuecomment-827158382

from numpy._typing import NDArray

from penalty_calc import calculate_editable_cost


def plot_stats_graph(graph_dir, move_history):
    os.makedirs(graph_dir, exist_ok=True)

    fig = plt.figure()  # over time
    # Plot hard_cost subplot in red
    ax1 = fig.add_subplot(2, 1, 1)  # 2 rows, 1 column, subplot 1
    ax1.plot(move_history['time'], move_history['hard_cost'], color='red', label='Hard Cost')
    ax1.set_ylabel('Hard Cost')

    # Plot soft_cost subplot in blue
    ax2 = fig.add_subplot(2, 1, 2)  # 2 rows, 1 column, subplot 2
    ax2.plot(move_history['time'], move_history['soft_cost'], color='blue', label='Soft Cost')
    ax2.set_ylabel('Soft Cost')
    ax2.set_xlabel('Time')

    # Set title for the entire figure
    fig.suptitle('Cost Over Time')
    fig.savefig(f'{graph_dir}/cost_over_time.png')

    plt.close(fig)

    fig = plt.figure()  # over moves
    # Plot hard_cost subplot in red
    ax1 = fig.add_subplot(2, 1, 1)  # 2 rows, 1 column, subplot 1
    ax1.plot(move_history.index, move_history['hard_cost'], color='red', label='Hard Cost')
    ax1.set_ylabel('Hard Cost')

    # Plot soft_cost subplot in blue
    ax2 = fig.add_subplot(2, 1, 2)  # 2 rows, 1 column, subplot 2
    ax2.plot(move_history.index, move_history['soft_cost'], color='blue', label='Soft Cost')
    ax2.set_ylabel('Soft Cost')
    ax2.set_xlabel('Moves')

    # Set title for the entire figure
    fig.suptitle('Cost Over Moves')
    fig.savefig(f'{graph_dir}/cost_over_moves.png')

    plt.close(fig)

    move_history.to_csv(f'{graph_dir}/move_history.csv', index=True)


def perturbation(gene: NDArray, max_gene, problem, editable_cost):
    for k in range(10):
        chosen_row = np.random.randint(0, len(gene))
        chosen_element = np.random.randint(0, 2)  # will we change the room or time?

        if max_gene[chosen_row, chosen_element] <= 0:
            chosen_value = 0
        else:
            chosen_value = np.random.randint(0, max_gene[chosen_row, chosen_element])

        gene[chosen_row, chosen_element] = chosen_value

    return gene


def iterated_local_search(gene: NDArray, max_gene, problem, max_ls_moves=1000, graph_dir=None, max_ls_time=1800):
    os.mkdir(graph_dir)

    move_history = pd.DataFrame(columns=['hard_cost', 'soft_cost', 'time'])
    start_time = time.time()

    chosen_gene = gene.copy()
    editable_cost = calculate_editable_cost(problem, gene)
    cost = editable_cost.calculate_total()

    move_history.loc[0] = {'hard_cost': cost[0], 'soft_cost': cost[1], 'time': 0}

    for i in range(1, 6):
        new_gene = chosen_gene.copy()
        new_gene = perturbation(new_gene, max_gene, problem, editable_cost)
        new_gene, new_cost = local_search(new_gene, max_gene, problem, max_ls_moves,
                                          os.path.join(graph_dir, f'ls_{i}'), max_ls_time)

        if new_cost <= cost:
            cost = new_cost
            chosen_gene = new_gene
            print(f'New best cost found: {cost}')
        else:
            print(f'No better solution found, perturbating...')

        move_history.loc[i] = {'hard_cost': cost[0], 'soft_cost': cost[1], 'time': time.time() - start_time}

    plot_stats_graph(graph_dir, move_history)
    return chosen_gene, cost
