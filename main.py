import numpy as np
import yaml

from costCalcuation.distributions.create_distribtion_helper import create_helper_for_distribution
from genetic_operators.parent_selection import get_parent_selection_method
from models.input.problem import Problem
from models.input.unavailability import Unavailability
from parse_input import parse_xml
from timetable_solver import TimetableSolver


def pre_process(problem: Problem):
    def distribution_filter(d):
        return not ((d.penalty == 0 and not d.required) or len(d.class_ids) <= 1)

    old_distribution_count = len(problem.distributions)
    problem.distributions = list(filter(distribution_filter, problem.distributions))
    new_distribution_count = len(problem.distributions)

    print("removed", old_distribution_count - new_distribution_count, "distributions for being redundant")

    removed_time_options = []
    removed_room_options = []
    remaining_closed_room_time_combinations = 0
    total_options_removed = 0

    # when a class is fixed, set the room to be unavailable during that time
    for c in problem.classes:
        c.pre_placed = True
        if c.is_fixed():
            if len(c.room_options) == 1:
                room = problem.get_room_by_id(c.room_options[0].id)
                room.unavailabilities.append(Unavailability(c.time_options[0].days, c.time_options[0].start,
                                                            c.time_options[0].length, c.time_options[0].weeks))

    # close room time combinations when room is unavailable
    for c in problem.classes:

        if len(c.room_options) == 0 or c.pre_placed:
            continue

        closed_room_time_combinations = np.zeros((len(c.room_options), len(c.time_options)), dtype=bool)

        for ro_index, ro in enumerate(c.room_options):
            room = problem.get_room_by_id(ro.id)
            room_unavailabilities = room.unavailabilities

            for to_index, to in enumerate(c.time_options):
                for ru in room_unavailabilities:
                    if not (
                            to.start >= (ru.start + ru.length) or
                            ru.start >= (to.start + to.length) or
                            not np.any(np.logical_and(to.days, ru.days)) or
                            not np.any(np.logical_and(to.weeks, ru.weeks))
                    ):
                        closed_room_time_combinations[ro_index, to_index] = True
                        break

        rows_to_remove = np.all(closed_room_time_combinations, axis=1)
        cols_to_remove = np.all(closed_room_time_combinations, axis=0)

        removed_room_options.extend([(c, c.room_options[i]) for i in np.where(rows_to_remove)[0]])
        removed_time_options.extend([(c, c.time_options[i]) for i in np.where(cols_to_remove)[0]])
        total_options_removed += np.count_nonzero(closed_room_time_combinations)

        closed_room_time_combinations = closed_room_time_combinations[~rows_to_remove, :]
        closed_room_time_combinations = closed_room_time_combinations[:, ~cols_to_remove]

        remaining_closed_room_time_combinations += np.count_nonzero(closed_room_time_combinations)

        c.room_options = [c.room_options[i] for i in np.where(~rows_to_remove)[0]]
        c.room_options_ids = [c.room_options_ids[i] for i in np.where(~rows_to_remove)[0]]
        c.time_options = [c.time_options[i] for i in np.where(~cols_to_remove)[0]]
        c.closed_room_time_combinations = closed_room_time_combinations

    print("removed", len(removed_room_options), "room options")
    print("removed", len(removed_time_options), "time options")
    print("removed", total_options_removed, "total room time combinations")
    print(remaining_closed_room_time_combinations, "closed room time combinations remaining")


if __name__ == "__main__":

    settings_file = open("settings.yaml", "r")
    settings = yaml.safe_load(settings_file)

    file_path = settings['input']
    problem = parse_xml(file_path)

    for d in problem.distributions:
        d.distribution_helper = create_helper_for_distribution(problem, d)

    # pre-processing
    pre_process(problem)

    solid_state = settings['solid_state']

    population_size = settings['hyperparams']['population_size']
    no_of_generations = settings['hyperparams']['no_of_generations']

    parent_selection = get_parent_selection_method(settings['hyperparams']['parent_selection'])

    mutation_chance = settings['hyperparams']['mutation_chance']
    crossover_ration = settings['hyperparams']['crossover_ratio']

    solver = TimetableSolver(problem,
                             solid_state=solid_state,
                             no_of_generations=no_of_generations,
                             population_size=population_size,
                             parent_selection=parent_selection,
                             mutation_chance=mutation_chance,
                             )

    solver.run()
