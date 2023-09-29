import numpy as np
from numpy.typing import NDArray

from models.input.clazz import Clazz
from models.input.problem import Problem


def calculate_total_penalty(problem: Problem, classes: list[Clazz], gene: NDArray):
    n = len(classes)

    times_chosen = [None] * n
    rooms_chosen = [None] * n

    rooms_chosen_idx = [0] * n

    room_penalties = np.empty(n)
    time_penalties = np.empty(n)

    for i in range(n):
        rooms_chosen_idx[i] = gene[i, 0].item()
        chosen_time_index = gene[i, 1].item()

        rooms_chosen[i] = None if rooms_chosen_idx[i] < 0 else classes[i].room_options[rooms_chosen_idx[i]]
        times_chosen[i] = classes[i].time_options[chosen_time_index]

        room_penalties[i] = 0 if rooms_chosen[i] is None else classes[i].room_options[rooms_chosen_idx[i]].penalty
        time_penalties[i] = classes[i].time_options[chosen_time_index].penalty

    rooms_bookings = np.zeros((len(problem.rooms), problem.nrWeeks, problem.nrDays, problem.slotsPerDay))

    for idx, room in enumerate(problem.rooms):
        room_mask = room.get_unavailability_mask(problem.nrWeeks, problem.nrDays, problem.slotsPerDay)
        rooms_bookings[idx][room_mask] = -1

    room_clash_count = 0

    for i, c in enumerate(classes):
        weeks = np.array(times_chosen[i].weeks)
        days = np.array(times_chosen[i].days)
        timeslots = np.full(problem.slotsPerDay, False)
        timeslots[times_chosen[i].start:times_chosen[i].start + times_chosen[i].length] = True

        mask = np.outer(np.outer(weeks, days), timeslots).reshape(
            (problem.nrWeeks, problem.nrDays, problem.slotsPerDay))

        room_clash_count += np.count_nonzero(rooms_bookings[rooms_chosen_idx[i]][mask])
        print(i)

    return room_penalties.sum(), time_penalties.sum()
