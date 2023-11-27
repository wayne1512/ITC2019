import numpy as np

from models.input.clazz import Clazz


def calculate_time_option_penalties(classes: list[Clazz], time_option_chosen_ids):
    soft = 0

    for i, c in enumerate(classes):
        soft += c.time_options[time_option_chosen_ids[i]].penalty

    return 0, soft


def calculate_time_option_penalties_array(classes: list[Clazz], time_option_chosen_ids):
    result = np.empty((len(classes), 2), dtype=int)

    for i, c in enumerate(classes):
        result[i] = 0, c.time_options[time_option_chosen_ids[i]].penalty

    return result


def calculate_time_option_penalty_for_single_class(clazz: Clazz, time_option_chosen_id):
    return 0, clazz.time_options[time_option_chosen_id].penalty
