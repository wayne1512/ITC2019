import numpy as np

from models.input.clazz import Clazz


def bool_string_to_bool_arr(s):
    return [bool(int(c)) for c in s]


def extract_class_list(problem):
    classes: list[Clazz] = []

    for course in problem.courses:
        for conf in course.configs:
            for sp in conf.subparts:
                classes += sp.classes

    return classes


def random_gene(maximums):
    r = (np.random.rand(*maximums.shape) * (maximums + 1)).astype(int)
    r = np.where(maximums < 0, -1, r)
    return r


def get_gene_maximums(classes: list[Clazz]):
    gene_maximums = [
        (len(c.room_options) - 1, len(c.time_options) - 1)  # possible -1 for those who dont need a room
        for c in classes
    ]

    return np.array(gene_maximums)


def sum_of_costs(n):
    return tuple(np.array(n).sum(0))
