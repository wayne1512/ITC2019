from numpy.typing import NDArray

from costCalcuation.clashes import calculate_clashes
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

    clash_penalties = calculate_clashes(problem, rooms_chosen_idx, times_chosen_idx)

    return sum_of_costs([room_penalties, time_penalties, clash_penalties])
