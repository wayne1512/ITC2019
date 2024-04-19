import os
import time

import pandas as pd
from matplotlib import pyplot as plt
from numpy._typing import NDArray

from penalty_calc import calculate_editable_cost, edit_cost


def plot_stats_graph(graph_dir, move_history):
    os.mkdir(graph_dir)

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


def local_search(gene: NDArray, max_gene, problem, max_moves=10000, graph_dir=None):
    move_history = pd.DataFrame(columns=['hard_cost', 'soft_cost', 'time'])
    start_time = time.time()

    editable_cost = calculate_editable_cost(problem, gene)
    cost = editable_cost.calculate_total()

    move_history.loc[0] = {'hard_cost': cost[0], 'soft_cost': cost[1], 'time': 0}

    moves_done = 0

    class_count = 0
    i = 0
    while class_count < len(gene):

        class_moved = False

        i = (i + 1) % len(gene)
        class_count += 1

        class_cost = editable_cost.blame_class(i)
        if class_cost[0] == 0:  # not involved in a HC:
            continue

        # N1 - change of room
        for j in range(max_gene[i, 0] - 1):

            new_gene = gene.copy()
            new_gene[i, 0] = (gene[i, 0] + 1 + j) % (max_gene[i, 0] + 1)

            new_gene_editable_cost = edit_cost(editable_cost, new_gene, [i])
            new_gene_cost = new_gene_editable_cost.calculate_total()

            if new_gene_cost[0] < cost[0]:
                gene = new_gene.copy()
                editable_cost = new_gene_editable_cost
                cost = new_gene_cost
                class_moved = True
                break

        # N2 - change of time
        if not class_moved:
            for j in range(max_gene[i, 1] - 1):

                new_gene = gene.copy()
                new_gene[i, 1] = (gene[i, 1] + 1 + j) % (max_gene[i, 1] + 1)

                new_gene_editable_cost = edit_cost(editable_cost, new_gene, [i])
                new_gene_cost = new_gene_editable_cost.calculate_total()

                if new_gene_cost[0] < cost[0]:
                    gene = new_gene.copy()
                    editable_cost = new_gene_editable_cost
                    cost = new_gene_cost
                    class_moved = True
                    break

        # N3 - change of room and time
        if not class_moved:
            for j in range(max_gene[i, 0]):
                for k in range(max_gene[i, 1]):
                    new_gene = gene.copy()
                    new_gene[i, 0] = (gene[i, 0] + 1 + j) % (max_gene[i, 0] + 1)
                    new_gene[i, 1] = (gene[i, 1] + 1 + k) % (max_gene[i, 1] + 1)

                    new_gene_editable_cost = edit_cost(editable_cost, new_gene, [i])
                    new_gene_cost = new_gene_editable_cost.calculate_total()

                    if new_gene_cost[0] < cost[0]:
                        gene = new_gene.copy()
                        editable_cost = new_gene_editable_cost
                        cost = new_gene_cost
                        class_moved = True
                        break
                if class_moved:
                    break

        if class_moved:
            class_count = 0
            moves_done += 1
            move_history.loc[moves_done] = \
                {'hard_cost': cost[0], 'soft_cost': cost[1], 'time': time.time() - start_time}

            if moves_done >= max_moves:
                break
            print(f"Class {i} was moved making the new cost: {cost}")

    if cost[0] > 0:
        print(f"Local search ended with {cost[0]} hard constraints not satisfied")
        plot_stats_graph(graph_dir, move_history)
        return gene, cost
    else:

        class_count = 0
        i = 0
        while class_count < len(gene):

            class_moved = False

            i = (i + 1) % len(gene)
            class_count += 1

            # N1 - change of room
            for j in range(max_gene[i, 0] - 1):

                new_gene = gene.copy()
                new_gene[i, 0] = (gene[i, 0] + 1 + j) % (max_gene[i, 0] + 1)

                new_gene_editable_cost = edit_cost(editable_cost, new_gene, [i])
                new_gene_cost = new_gene_editable_cost.calculate_total()

                if new_gene_cost < cost:
                    gene = new_gene.copy()
                    editable_cost = new_gene_editable_cost
                    cost = new_gene_cost
                    class_moved = True
                    break

            # N2 - change of time
            if not class_moved:
                for j in range(max_gene[i, 1] - 1):

                    new_gene = gene.copy()
                    new_gene[i, 1] = (gene[i, 1] + 1 + j) % (max_gene[i, 1] + 1)

                    new_gene_editable_cost = edit_cost(editable_cost, new_gene, [i])
                    new_gene_cost = new_gene_editable_cost.calculate_total()

                    if new_gene_cost < cost:
                        gene = new_gene.copy()
                        editable_cost = new_gene_editable_cost
                        cost = new_gene_cost
                        class_moved = True
                        break

            # N3 - change of room and time
            if not class_moved:
                for j in range(max_gene[i, 0]):
                    for k in range(max_gene[i, 1]):
                        new_gene = gene.copy()
                        new_gene[i, 0] = (gene[i, 0] + 1 + j) % (max_gene[i, 0] + 1)
                        new_gene[i, 1] = (gene[i, 1] + 1 + k) % (max_gene[i, 1] + 1)

                        new_gene_editable_cost = edit_cost(editable_cost, new_gene, [i])
                        new_gene_cost = new_gene_editable_cost.calculate_total()

                        if new_gene_cost < cost:
                            gene = new_gene.copy()
                            editable_cost = new_gene_editable_cost
                            cost = new_gene_cost
                            class_moved = True
                            break
                    if class_moved:
                        break

            if class_moved:
                class_count = 0
                moves_done += 1
                move_history.loc[moves_done] = \
                    {'hard_cost': cost[0], 'soft_cost': cost[1], 'time': time.time() - start_time}

                if moves_done >= max_moves:
                    break
                print(f"Class {i} was moved making the new cost: {cost}")
    plot_stats_graph(graph_dir, move_history)
    return gene, cost
