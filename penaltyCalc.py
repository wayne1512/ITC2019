from numpy.typing import NDArray

from costCalcuation.clashes import calculate_clashes
from costCalcuation.roomOptionPenalty import calculate_room_option_penalties
from costCalcuation.timeOptionPenalty import calculate_time_option_penalties
from models.input.clazz import Clazz
from models.input.problem import Problem
from util import sum_of_costs


def calculate_total_cost(problem: Problem, classes: list[Clazz], gene: NDArray):
    n = len(classes)

    rooms_chosen_idx = gene[:, 0]
    room_penalties = calculate_room_option_penalties(classes, rooms_chosen_idx)

    times_chosen_idx = gene[:, 1]
    time_penalties = calculate_time_option_penalties(classes, times_chosen_idx)

    clash_penalties = calculate_clashes(problem, classes, rooms_chosen_idx, times_chosen_idx)

    return sum_of_costs([room_penalties, time_penalties, clash_penalties])
