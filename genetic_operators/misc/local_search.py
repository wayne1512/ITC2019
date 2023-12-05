import time

from penalty_calc import calculate_editable_cost, edit_cost


def local_search(gene, max_gene, problem, max_iter=25):
    editable_cost = calculate_editable_cost(problem, gene)

    best_gene = gene
    best_gene_cost = editable_cost.calculate_total()
    print("before local search: ", best_gene_cost)

    for i in range(max_iter):
        new_gene, new_gene_cost = local_search_iteration(best_gene, max_gene, problem)
        if new_gene_cost < best_gene_cost:
            best_gene = new_gene.copy()
            best_gene_cost = new_gene_cost
        else:
            break

    print("after local search: ", best_gene_cost)


    return best_gene, best_gene_cost


def local_search_iteration(gene, max_gene, problem):
    editable_cost = calculate_editable_cost(problem, gene)

    best_gene = gene
    best_gene_cost = editable_cost.calculate_total()
    print("before local search iter: ", best_gene_cost)

    start_time = time.time()

    for i in range(len(gene)):
        # change of room
        for j in range(max_gene[i, 0]):

            if problem.classes[i].closed_room_time_combinations is not None and \
                    problem.classes[i].closed_room_time_combinations[j, gene[i, 1]]:
                continue  # if the room time combination is closed, skip checking it

            new_gene = gene.copy()
            new_gene[i, 0] = j

            new_gene_cost = edit_cost(editable_cost, new_gene, [i]).calculate_total()

            if new_gene_cost < best_gene_cost:
                best_gene = new_gene.copy()
                best_gene_cost = new_gene_cost

        # change of time
        for j in range(max_gene[i, 1]):

            if problem.classes[i].closed_room_time_combinations is not None and \
                    problem.classes[i].closed_room_time_combinations[gene[i, 0], j]:
                continue  # if the room time combination is closed, skip checking it

            new_gene = gene.copy()
            new_gene[i, 1] = j
            new_gene_cost = edit_cost(editable_cost, new_gene, [i]).calculate_total()
            if new_gene_cost < best_gene_cost:
                best_gene = new_gene.copy()
                best_gene_cost = new_gene_cost

    print("after local search iter: ", best_gene_cost)
    print("local search iter time: ", time.time() - start_time)

    return best_gene, best_gene_cost
