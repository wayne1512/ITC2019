from collections import deque

from costCalcuation.distributions.double_booking import DoubleBookingHelper
from solution_search import SolutionSearch


class AC3:
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

    def supports(self, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
        for constraint in self.constraints[class_row_i][class_row_j]:
            if not constraint(self, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
                return False  # if one of the constraints is not satisfied, return False
        return True

    def revise(self, Vi, Vj, debugLevel=0):

        deleted = False

        for Vi_option in range(self.solution_search.options_per_class[Vi]):
            if self.solution_search.decision_table[Vi][Vi_option] != 0:
                continue

            found = False
            for Vj_option in range(self.solution_search.options_per_class[Vj]):

                if self.solution_search.decision_table[Vj][Vj_option] != 0:
                    continue

                if self.supports(Vi, Vj, Vi_option, Vj_option):
                    found = True
                    break
            if not found:

                if debugLevel >= 3:
                    print(f"revise: Vi: {Vi}, Vi_option: {Vi_option} was closed by Vj: {Vj}")

                self.solution_search.decision_table[Vi][Vi_option] = -1
                deleted = True

        return deleted

    def apply(self, debugLevel=0):

        step_counter = 0  # used for debugLevel >= 1

        Q = deque()

        for Vi in range(self.solution_search.decision_table.shape[0]):
            for Vj in range(self.solution_search.decision_table.shape[0]):
                R_Vi_Vj = self.constraints[Vi][Vj]
                if len(R_Vi_Vj) > 0:
                    Q.append((Vi, Vj))

        print(f"finished creating Q with {len(Q)} elements")

        while len(Q) > 0:
            Vi, Vj = Q.popleft()
            if debugLevel >= 3:
                print("processing ", str(Vi), str(Vj), " current Q size: ", len(Q))
            if self.revise(Vi, Vj, debugLevel=debugLevel):
                if 0 not in self.solution_search.decision_table[Vi]:
                    print(f"Vi: {Vi} has no solution after closing options inconsistent with {Vj}")
                    raise Exception("No solution")
                else:
                    for Vk in range(self.solution_search.decision_table.shape[0]):
                        if Vk != Vj:
                            if (Vk, Vi) not in Q:
                                if len(self.constraints[Vk][Vi]) > 0:
                                    Q.append((Vk, Vi))

            if debugLevel >= 2:
                step_counter += 1
                if step_counter % 100 == 0:
                    print(f"Q size: {len(Q)}")
            elif debugLevel >= 1:
                step_counter += 1
                if step_counter % 10000 == 0:
                    print(f"Q size: {len(Q)}")

        return True
