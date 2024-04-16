from numpy.typing import NDArray

from costCalcuation.distributions.double_booking import DoubleBookingHelper
from costCalcuation.distributions.same_attendees_distribution_helper import SameAttendeesDistributionHelper
from costCalcuation.room_option_penalty import calculate_room_option_penalties, \
    calculate_room_option_penalties_array, calculate_room_option_penalty_for_single_class
from costCalcuation.time_option_penalty import calculate_time_option_penalties, \
    calculate_time_option_penalties_array, calculate_time_option_penalty_for_single_class
from costCalcuation.unavailable_room import UnavailableRoomHelper
from models.input.distribution import Distribution
from models.input.problem import Problem
from util import sum_of_costs


def calculate_total_cost_including_student_conflicts(problem: Problem, gene: NDArray, student_classes: dict):
    total_cost = calculate_total_cost(problem, gene)
    student_conflicts = calculate_student_conflicts(problem, gene, student_classes)
    return tuple(map(sum, zip(total_cost, student_conflicts)))


def calculate_student_conflicts(problem: Problem, gene: NDArray, student_classes: dict):
    student_violations = (0, 0)

    for s_id, c_ids in student_classes.items():
        dist = Distribution('SameAttendees', False, 1, c_ids)
        helper = dist.distribution_helper = SameAttendeesDistributionHelper(problem, dist)
        count = helper.calculate_clashes(gene[:, 0], gene[:, 1])
        student_violations = (0, student_violations[1] + count[1])

    return 0, (student_violations[1] * problem.optimization.student)

def calculate_total_cost(problem: Problem, gene: NDArray):
    n = len(problem.classes)

    rooms_chosen_idx = gene[:, 0]
    room_penalties = calculate_room_option_penalties(problem.classes, rooms_chosen_idx)
    room_penalties = (room_penalties[0], room_penalties[1] * problem.optimization.room)

    times_chosen_idx = gene[:, 1]
    time_penalties = calculate_time_option_penalties(problem.classes, times_chosen_idx)
    time_penalties = (time_penalties[0], time_penalties[1] * problem.optimization.time)

    double_booking_helper = DoubleBookingHelper(problem)
    double_booking_penalties = double_booking_helper.calculate_clashes(rooms_chosen_idx, times_chosen_idx)

    unavailable_room_helper = UnavailableRoomHelper(problem)
    unavailable_room_penalties = unavailable_room_helper.calculate_clashes(rooms_chosen_idx, times_chosen_idx)

    dist_penalties_arr = [d.distribution_helper.calculate_clashes(rooms_chosen_idx, times_chosen_idx) for d in
                          problem.distributions]
    distribution_penalties = sum_of_costs(
        dist_penalties_arr)
    distribution_penalties = (distribution_penalties[0], distribution_penalties[1] * problem.optimization.distribution)

    return sum_of_costs(
        [room_penalties, time_penalties, double_booking_penalties, unavailable_room_penalties, distribution_penalties])


def calculate_editable_cost(problem: Problem, gene: NDArray):
    rooms_chosen_idx = gene[:, 0]
    room_penalties = calculate_room_option_penalties_array(problem.classes, rooms_chosen_idx)

    times_chosen_idx = gene[:, 1]
    time_penalties = calculate_time_option_penalties_array(problem.classes, times_chosen_idx)

    double_booking_helper = DoubleBookingHelper(problem)
    double_booking_penalties = double_booking_helper.calculate_clashes_editable(rooms_chosen_idx, times_chosen_idx)

    unavailable_room_helper = UnavailableRoomHelper(problem)
    unavailable_room_penalties = unavailable_room_helper.calculate_clashes_editable(rooms_chosen_idx, times_chosen_idx)

    dist_penalties_arr = [d.distribution_helper.calculate_clashes(rooms_chosen_idx, times_chosen_idx) for d in
                          problem.distributions]

    return EditablePenaltyCalculation(problem, room_penalties, time_penalties, double_booking_penalties,
                                      unavailable_room_penalties, dist_penalties_arr)


def edit_cost(editable_penalties, gene: NDArray, changed_indexes):
    rooms_chosen_idx = gene[:, 0]
    room_penalties = editable_penalties.room_penalties.copy()
    times_chosen_idx = gene[:, 1]
    time_penalties = editable_penalties.time_penalties.copy()

    unavailable_room_penalties = editable_penalties.unavailable_room_penalties.copy()

    unavailable_room_helper = UnavailableRoomHelper(editable_penalties.problem)

    for i in changed_indexes:
        room_penalties[i] = calculate_room_option_penalty_for_single_class(editable_penalties.problem.classes[i],
                                                                           rooms_chosen_idx[i])
        time_penalties[i] = calculate_time_option_penalty_for_single_class(editable_penalties.problem.classes[i],
                                                                           times_chosen_idx[i])
        unavailable_room_penalties[i] = unavailable_room_helper.count_violation_for_single_class(
            editable_penalties.problem.classes[i], rooms_chosen_idx[i], times_chosen_idx[i])

    changed_class_ids = [editable_penalties.problem.classes[i].id for i in changed_indexes]

    double_booking_helper = DoubleBookingHelper(editable_penalties.problem)
    double_booking_penalties = double_booking_helper.edit_calculation(rooms_chosen_idx, times_chosen_idx,
                                                                      editable_penalties.double_booking_penalties.copy(),
                                                                      changed_indexes, changed_class_ids)

    dist_penalties_arr = editable_penalties.distribution_penalties.copy()
    for i, d in enumerate(editable_penalties.problem.distributions):
        if any(c_id in changed_class_ids for c_id in d.class_ids):
            dist_penalties_arr[i] = d.distribution_helper.calculate_clashes(rooms_chosen_idx, times_chosen_idx)

    return EditablePenaltyCalculation(editable_penalties.problem, room_penalties, time_penalties,
                                      double_booking_penalties, unavailable_room_penalties,
                                      dist_penalties_arr)


class EditablePenaltyCalculation:
    def __init__(self, problem, room_penalties, time_penalties, double_booking_penalties, unavailable_room_penalties,
                 distribution_penalties):
        self.problem = problem
        self.room_penalties = room_penalties
        self.time_penalties = time_penalties
        self.double_booking_penalties = double_booking_penalties
        self.unavailable_room_penalties = unavailable_room_penalties
        self.distribution_penalties = distribution_penalties

    def calculate_total(self):
        room_penalties_cost = sum_of_costs(self.room_penalties)
        room_penalties_cost = (room_penalties_cost[0], room_penalties_cost[1] * self.problem.optimization.room)

        time_penalties_cost = sum_of_costs(self.time_penalties)
        time_penalties_cost = (time_penalties_cost[0], time_penalties_cost[1] * self.problem.optimization.time)

        distribution_penalties_cost = sum_of_costs(self.distribution_penalties)
        distribution_penalties_cost = (distribution_penalties_cost[0], distribution_penalties_cost[1]
                                       * self.problem.optimization.distribution)

        return sum_of_costs([room_penalties_cost, time_penalties_cost,
                             (len(self.double_booking_penalties), 0),
                             sum_of_costs(self.unavailable_room_penalties),
                             distribution_penalties_cost])
