from numpy.typing import NDArray

from costCalcuation.distributions.double_booking import DoubleBookingHelper
from costCalcuation.room_option_penalty import calculate_room_option_penalties
from costCalcuation.time_option_penalty import calculate_time_option_penalties
from models.input.problem import Problem
from util import sum_of_costs


def calculate_total_cost(problem: Problem, gene: NDArray):
    n = len(problem.classes)

    rooms_chosen_idx = gene[:, 0]
    room_penalties = calculate_room_option_penalties(problem.classes, rooms_chosen_idx)

    times_chosen_idx = gene[:, 1]
    time_penalties = calculate_time_option_penalties(problem.classes, times_chosen_idx)

    double_booking_helper = DoubleBookingHelper(problem)
    double_booking_penalties = double_booking_helper.calculate_clashes(rooms_chosen_idx, times_chosen_idx)

    dist_penalties_arr = [d.distribution_helper.calculate_clashes(rooms_chosen_idx, times_chosen_idx) for d in
                          problem.distributions]
    distribution_penalties = sum_of_costs(
        dist_penalties_arr)

    return sum_of_costs([room_penalties, time_penalties, double_booking_penalties, distribution_penalties])
