from models.input.clazz import Clazz


def calculate_time_option_penalties(classes: list[Clazz], time_option_chosen_ids):
    soft = 0

    for i, c in enumerate(classes):
        soft += c.time_options[time_option_chosen_ids[i]].penalty

    return 0, soft
