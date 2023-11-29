import numpy as np

from costCalcuation.distributions.double_booking import DoubleBookingHelper


class InitialTimetableTreeSearchSolver:
    def __init__(self, solution_search):
        self.solution_search = solution_search

    def close_downwards_options(self, current_row, current_option):
        mask = np.zeros_like(self.solution_search.decision_table, dtype=bool)

        DoubleBookingHelper(self.solution_search.problem).close_downwards_option(self.solution_search, current_row,
                                                                                 current_option, mask)

        for d in self.solution_search.problem.distributions:
            if d.required and self.solution_search.classes[current_row].id in d.class_ids:
                d.distribution_helper.close_downwards_option(self.solution_search, current_row, current_option, mask)

        mask = mask & (self.solution_search.decision_table == 0)
        self.solution_search.decision_table[mask] = (-current_row - 2)  # close

    def solve(self):
        current_row = 0
        current_option = 0

        while current_row < len(self.solution_search.classes):
            # check if there is any row where all the options are closed - in which case we are ready to backtrack
            while np.any(np.all(self.solution_search.decision_table[current_row:], axis=1)):
                # backtrack
                self.solution_search.decision_table[self.solution_search.decision_table <= (-current_row - 1)] = 0
                print("backtrack from " + str(current_row) + " to " + str(current_row - 1))
                current_row -= 1
                option_to_close = np.where(self.solution_search.decision_table[current_row] == 1)
                self.solution_search.decision_table[current_row][option_to_close] = (-current_row - 1)

            # class with the least open options
            next_class_offset = np.argmax(np.count_nonzero(self.solution_search.decision_table[current_row:], axis=1))
            swap_row = next_class_offset + current_row
            self.solution_search.swap_rows(current_row, swap_row)

            open_options = np.where(self.solution_search.decision_table[current_row] == 0)[0]
            current_option = open_options[0]

            self.solution_search.decision_table[current_row, current_option] = 1

            self.close_downwards_options(current_row, current_option)

            print("proceeded from " + str(current_row) + " to " + str(current_row + 1))

            current_row += 1
