import numpy as np


def bool_string_to_bool_arr(s):
    return [bool(int(c)) for c in s]


def bool_arr_to_string(b):
    return ''.join([str(1 if b else 0) for b in b])


def extract_class_list(problem):
    classes: list = []

    for course in problem.courses:
        for conf in course.configs:
            for sp in conf.subparts:
                classes += sp.classes

    return classes


def random_gene(maximums, problem=None):
    r = (np.random.rand(*maximums.shape) * (maximums + 1)).astype(int)

    if problem is not None:
        for i, c in enumerate(problem.classes):

            if c.is_fixed():
                r[i] = (0, 0)
                continue

            # is not none handles classes with no rooms
            while c.closed_room_time_combinations is not None and \
                    c.closed_room_time_combinations[r[i, 0], r[i, 1]]:
                # if the current room time combination is closed, choose a new one
                r[i] = (np.random.rand() * (maximums[i] + 1)).astype(int)

    r = np.where(maximums < 0, -1, r)
    return r


def get_gene_maximums(classes: list):
    gene_maximums = [
        (len(c.room_options) - 1, len(c.time_options) - 1)  # possible -1 for those who dont need a room
        for c in classes
    ]

    return np.array(gene_maximums)


def sum_of_costs(n):
    return tuple(np.array(n).sum(0))


def generate_timeslots_mask(weeks, days, start, length, nr_weeks, nr_days, slots_per_day):
    weeks = np.array(weeks)
    days = np.array(days)
    timeslots = np.full(slots_per_day, False)
    timeslots[start:start + length] = True

    mask = np.outer(np.outer(weeks, days), timeslots).reshape(
        (nr_weeks, nr_days, slots_per_day))

    return mask
