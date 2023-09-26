import numpy as np
from numpy.typing import NDArray

from models.input.clazz import Clazz


def calculate_total_penalty(classes: list[Clazz], gene: NDArray):
    n = len(classes)

    room_penalties = np.empty(n)
    time_penalties = np.empty(n)

    for i in range(n):
        chosen_room_index = gene[i, 0].item()
        chosen_time_index = gene[i, 1].item()

        room_penalties[i] = 0 if chosen_room_index < 0 else classes[i].room_options[chosen_room_index].penalty
        time_penalties[i] = 0 if chosen_time_index < 0 else classes[i].time_options[chosen_time_index].penalty

    np.copy(gene)
