from models.input.clazz import Clazz


def calculate_room_option_penalties(classes: list[Clazz], rooms_option_chosen_ids):
    soft = 0

    for i, c in enumerate(classes):
        if rooms_option_chosen_ids[i] >= 0:
            soft += c.room_options[rooms_option_chosen_ids[i]].penalty

    return 0, soft
