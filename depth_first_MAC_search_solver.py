import time
from collections import deque

import numpy as np

from costCalcuation.distributions.double_booking import DoubleBookingHelper


class DepthFirstSearchMACSolver:
    def __init__(self, solution_search):
        self.solution_search = solution_search

        self.Q = deque()

        self.constraints = [
            [
                []
                for j in range(self.solution_search.decision_table.shape[0])
            ]
            for i in range(self.solution_search.decision_table.shape[0])
        ]

        constraints_for_double_booking = DoubleBookingHelper(self.solution_search.problem).to_ac4_constraints()
        for class_i_id, class_j_id, f in constraints_for_double_booking:
            class_i_index = (
                next((i for i, c in enumerate(self.solution_search.problem.classes) if c.id == class_i_id), None))
            class_j_index = (
                next((i for i, c in enumerate(self.solution_search.problem.classes) if c.id == class_j_id), None))
            self.constraints[class_i_index][class_j_index].append(f)

        for d in self.solution_search.problem.distributions:
            if d.required:
                constraints_for_d = d.distribution_helper.to_ac4_constraints()
                if constraints_for_d is None:
                    continue
                for class_i_id, class_j_id, f in constraints_for_d:
                    class_i_index = (
                        next((i for i, c in enumerate(self.solution_search.problem.classes) if c.id == class_i_id),
                             None))
                    class_j_index = (
                        next((i for i, c in enumerate(self.solution_search.problem.classes) if c.id == class_j_id),
                             None))
                    self.constraints[class_i_index][class_j_index].append(f)

    def close_downwards_options(self, current_row, current_option, debug_level=0):

        if debug_level >= 4:
            print(f"close_downwards_options for row {current_row} option {current_option}")

        mask = np.zeros_like(self.solution_search.decision_table, dtype=bool)

        DoubleBookingHelper(self.solution_search.problem).close_downwards_option(self.solution_search, current_row,
                                                                                 current_option, mask)

        for d in self.solution_search.problem.distributions:
            if d.required and self.solution_search.classes[current_row].id in d.class_ids:
                d.distribution_helper.close_downwards_option(self.solution_search, current_row, current_option, mask)

        mask = mask & (self.solution_search.decision_table == 0)
        self.solution_search.decision_table[mask] = (-current_row - 2)  # close

        # add arcs to queue
        for i in range(current_row + 1, self.solution_search.decision_table.shape[0]):
            if i != current_row:
                self.Q.append((i, current_row))
        if debug_level >= 3:
            print(f"AC3 queue: {len(self.Q)} after closing downwards options for row {current_row} option"
                  f" {current_option}")
        self.propagate_ac3(current_row, debug_level=debug_level)

    def supports(self, class_row_i, class_row_j, class_row_i_option, class_row_j_option, debug_level=0):
        if debug_level >= 5:
            print(f"checking supports: {class_row_i} {class_row_j} {class_row_i_option} {class_row_j_option}")
        for constraint in self.constraints[class_row_i][class_row_j]:
            if not constraint(self, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
                return False  # if one of the constraints is not satisfied, return False
        return True

    def revise(self, Vi, Vj, current_row, debugLevel=0):

        deleted = False

        for Vi_option in range(self.solution_search.options_per_class[Vi]):
            if self.solution_search.decision_table[Vi][Vi_option] != 0:
                continue

            found = False
            for Vj_option in range(self.solution_search.options_per_class[Vj]):

                if self.solution_search.decision_table[Vj][Vj_option] < 0:
                    continue

                if self.supports(Vi, Vj, Vi_option, Vj_option, debug_level=debugLevel):
                    found = True
                    break
            if not found:

                if debugLevel >= 3:
                    print(f"revise: Vi: {Vi}, Vi_option: {Vi_option} was closed by Vj: {Vj}")

                self.solution_search.decision_table[Vi][Vi_option] = (-current_row - 2)  # close
                deleted = True

        return deleted

    def propagate_ac3(self, current_row, debug_level=0):
        while len(self.Q) > 0:

            if debug_level >= 3 or (debug_level >= 1 and len(self.Q) % 10000 == 0):
                print("AC3 queue: ", len(self.Q))

            Vi, Vj = self.Q.popleft()
            if debug_level >= 4:
                print(f"revise: Vi: {Vi}, Vj: {Vj}")

            if self.revise(Vi, Vj, current_row, debugLevel=debug_level):

                # check if there is any row where all the options are closed - in which case we are ready to backtrack
                if not np.any(self.solution_search.decision_table[Vi] == 0):
                    return False

                for Vk in range(current_row + 1, self.solution_search.decision_table.shape[0]):
                    if Vk != Vi:
                        if len(self.constraints[Vi][Vk]) > 0:
                            if (Vk, Vi) not in self.Q:
                                self.Q.append((Vk, Vi))
        return True

    def solve(self, debug_level=0, choose_most_constrained_class=True, randomize_option=False, max_operations=-1,
              max_backtracks=-1, skip_initial_ac3=False):

        operation_count = 0
        backtrack_count = 0
        operation_history = []
        start_time = time.time()

        current_row = 0
        current_option = 0

        self.Q.clear()

        if not skip_initial_ac3:  # save time by doing ac3 beforehand, useful for repeats since the initial ac3 can be reused
            for Vi in range(self.solution_search.decision_table.shape[0]):
                for Vj in range(self.solution_search.decision_table.shape[0]):
                    R_Vi_Vj = self.constraints[Vi][Vj]
                    if len(R_Vi_Vj) > 0:
                        self.Q.append((Vi, Vj))

            if self.propagate_ac3(-1, debug_level):  # start with an initial AC3
                if self.solution_search.decision_table[self.solution_search.decision_table <= 0].all():
                    print("AC3 failed")
                    raise Exception("No solution")

        while current_row < len(self.solution_search.classes):

            # check if there is any row where all the options are closed - in which case we are ready to backtrack
            while np.any(np.all(self.solution_search.decision_table[current_row:], axis=1)):

                if (max_backtracks != -1 and backtrack_count >= max_backtracks) or (
                        max_operations != -1 and operation_count >= max_operations):
                    break  # no more backtracks allowed

                # backtrack
                self.solution_search.decision_table[self.solution_search.decision_table <= (-current_row - 1)] = 0
                if debug_level >= 2:
                    print("backtrack from " + str(current_row) + " to " + str(current_row - 1))

                current_row -= 1

                if current_row < 0:
                    raise Exception("Critical failure: Backtracked too much - something is wrong!")

                # append an object to the history of operations array
                operation_history.append({'current_row': current_row, 'time': time.time() - start_time})
                backtrack_count += 1
                operation_count += 1

                option_to_close = np.where(self.solution_search.decision_table[current_row] == 1)
                self.solution_search.decision_table[current_row][option_to_close] = (-current_row - 1)

            if max_backtracks != -1 and backtrack_count >= max_backtracks:
                break  # exceeded number of backtracks allowed - so we stop

            if max_operations != -1 and operation_count >= max_operations:
                break  # exceeded number of operations allowed - so we stop

            # class with the least open options
            if choose_most_constrained_class:
                next_class_offset = np.argmax(
                    np.count_nonzero(self.solution_search.decision_table[current_row:], axis=1))
                swap_row = next_class_offset + current_row

                self.solution_search.swap_rows(current_row, swap_row)
                self.constraints[current_row], self.constraints[swap_row] = (
                    self.constraints[swap_row], self.constraints[current_row])

                for row in self.constraints:
                    row[current_row], row[swap_row] = row[swap_row], row[current_row]

            open_options = np.where(self.solution_search.decision_table[current_row] == 0)[0]

            if randomize_option:
                np.random.shuffle(open_options)
            current_option = open_options[0]

            self.solution_search.decision_table[current_row, open_options] = (-current_row - 2)  # close other options
            self.solution_search.decision_table[current_row, current_option] = 1

            # # these arcs are not required since we are using close downwards options
            # # to kickstart the AC3 propagation chain
            # for Vj in range(self.solution_search.decision_table.shape[0]):
            #     if Vj != current_row:
            #         if len(self.constraints[Vj][current_row]) > 0:
            #             self.Q.append((Vj, current_row))

            self.close_downwards_options(current_row, current_option, debug_level=debug_level)

            if debug_level >= 2:
                print("proceeded from " + str(current_row) + " to " + str(current_row + 1))
            elif debug_level >= 1 and current_row % 100 == 0:
                print("proceeded from " + str(current_row) + " to " + str(current_row + 1))
            current_row += 1

            operation_count += 1
            operation_history.append({'current_row': current_row, 'time': time.time() - start_time})

        return {
            'success': len(self.solution_search.classes) == current_row,
            'operation_count': operation_count,
            'backtrack_count': backtrack_count,
            'operation_history': operation_history,
            'time': time.time() - start_time
        }
