import yaml

import timetable_solver
from costCalcuation.distributions.create_distribtion_helper import create_helper_for_distribution
from parse_input import parse_xml

if __name__ == "__main__":

    settings_file = open("settings.yaml", "r")
    settings = yaml.safe_load(settings_file)

    file_path = settings['input']
    problem = parse_xml(file_path)

    for d in problem.distributions:
        d.distribution_helper = create_helper_for_distribution(problem, d)

    population_size = settings['hyperparams']['population_size']
    no_of_generations = settings['hyperparams']['no_of_generations']

    timetable_solver.run(problem,
                         no_of_generations=no_of_generations,
                         population_size=population_size)
