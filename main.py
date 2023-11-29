import yaml

from costCalcuation.distributions.create_distribtion_helper import create_helper_for_distribution
from genetic_operators.parent_selection import *
from parse_input import parse_xml
from timetable_solver import TimetableSolver

if __name__ == "__main__":

    settings_file = open("settings.yaml", "r")
    settings = yaml.safe_load(settings_file)

    file_path = settings['input']
    problem = parse_xml(file_path)

    for d in problem.distributions:
        d.distribution_helper = create_helper_for_distribution(problem, d)

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
