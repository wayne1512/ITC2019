import numpy as np

from costCalcuation.distributions.double_booking import DoubleBookingHelper
from solution_search import SolutionSearch


class AC4:
    def __init__(self, solution_search: SolutionSearch):
        self.solution_search: SolutionSearch = solution_search
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

        self.support_set = [
            [
                []
                for v_i in range(self.solution_search.options_per_class[i])
            ]
            for i in range(self.solution_search.decision_table.shape[0])
        ]

        self.counter = [
            [
                [
                    0
                    for v_i in range(self.solution_search.options_per_class[i])
                ]
                for j in range(self.solution_search.decision_table.shape[0])
            ]
            for i in range(self.solution_search.decision_table.shape[0])
        ]

    def supports(self, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
        for constraint in self.constraints[class_row_i][class_row_j]:
            if not constraint(self, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
                return False  # if one of the constraints is not satisfied, return False
        return True

    def apply(self):

        # (class_row_i,class_row_j)->Ac4Constraint[]

        # an array of (class row index, option index) pairs
        # ex: (5,1) means class index 5, option 1
        deletion_stream = []

        for i in range(self.solution_search.decision_table.shape[0]):
            closed_options = np.where(
                self.solution_search.decision_table[i, :self.solution_search.options_per_class[i]] == -1
            )
            for option in closed_options[0]:
                deletion_stream.append((i, option))

        for Vi in range(self.solution_search.decision_table.shape[0]):
            for Vj in range(self.solution_search.decision_table.shape[0]):
                print("initializing AC4 support structures: Vi", str(Vi), "Vj", str(Vj))
                R_Vi_Vj = self.constraints[Vi][Vj]
                if len(R_Vi_Vj) > 0:
                    for Vi_option in range(self.solution_search.options_per_class[Vi]):
                        total = 0
                        for Vj_option in range(self.solution_search.options_per_class[Vj]):
                            if self.supports(Vi, Vj, Vi_option, Vj_option):
                                total += 1
                                self.support_set[Vj][Vj_option].append((Vi, Vi_option))
                        if total == 0:
                            # no support for (Vi, Vi_option) so we close it
                            self.solution_search.decision_table[Vi][Vi_option] = -1
                            deletion_stream.append((Vi, Vi_option))

                            if 0 not in self.solution_search.decision_table[Vi]:
                                raise Exception("No solution")

                        else:
                            self.counter[Vi][Vj][Vi_option] = total

        while len(deletion_stream) > 0:
            Vi, Vi_option = deletion_stream.pop()
            print("closing ", str(Vi), str(Vi_option))

            print("deletion stream length", str(len(deletion_stream)))

            for Vj, Vj_option in self.support_set[Vi][Vi_option]:
                self.counter[Vj][Vi][Vj_option] -= 1
                if self.counter[Vj][Vi][Vj_option] == 0:
                    self.solution_search.decision_table[Vj][Vj_option] = -1
                    deletion_stream.append((Vj, Vj_option))
                    if 0 not in self.solution_search.decision_table[Vj]:
                        raise Exception("No solution")

        return True
