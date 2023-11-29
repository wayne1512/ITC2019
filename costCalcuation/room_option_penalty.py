import numpy as np

from models.input.clazz import Clazz


def calculate_room_option_penalties(classes: list[Clazz], rooms_option_chosen_ids):
    soft = 0

    for i, c in enumerate(classes):
        if rooms_option_chosen_ids[i] >= 0:
            soft += c.room_options[rooms_option_chosen_ids[i]].penalty

    return 0, soft


def calculate_room_option_penalties_array(classes: list[Clazz], rooms_option_chosen_ids):
    result = np.empty((len(classes), 2), dtype=int)

    for i, c in enumerate(classes):
        if rooms_option_chosen_ids[i] >= 0:
            result[i] = 0, c.room_options[rooms_option_chosen_ids[i]].penalty
        else:
            result[i] = 0, 0

    return result


def calculate_room_option_penalty_for_single_class(clazz: Clazz, room_option_chosen_id):
    if room_option_chosen_id >= 0:
        return 0, clazz.room_options[room_option_chosen_id].penalty
    else:
        return 0, 0
