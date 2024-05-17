#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import time

from parse_input import parse_itc2007_post_enrolment, parse_itc2007_curriculum_based, parse_xml
from random_student_sectioning import RandomStudentSectioning
from solution_to_xml import output_itc2007_cb, generate_xml
from timetable_solver import TimetableSolver

# In[ ]:


itc2007_track2_path = '.\\Datasets\\post'
itc2007_track3_path = '.\\Datasets\\curriculum'
itc2019_path = '.\\Datasets\\2019'


def get_all_files(path):
    return [os.path.join(dirpath, file) for dirpath, _, filenames in os.walk(path) for file in filenames]


itc2007_track2_files = get_all_files(itc2007_track2_path)
itc2007_track3_files = get_all_files(itc2007_track3_path)
itc2019_files = get_all_files(itc2019_path)


def filter_files_by_name(files, queries):
    # check if filename matches query
    return [file for file in files if file.split('\\')[-1].split('.')[0] in queries]


def parse_problem(dataset, instance_path):
    if dataset == 'itc2007_track2':
        return parse_itc2007_post_enrolment(instance_path)
    elif dataset == 'itc2007_track3':
        return parse_itc2007_curriculum_based(instance_path)
    elif dataset == 'itc2019':
        return parse_xml(instance_path)


# In[ ]:


graph_interval = 1


def run_experiment_for_dataset(dataset, files, experiment_name, repetitions, ga_params):
    output_path = f'output/{experiment_name}_{dataset}_{time.strftime("%Y%m%d-%H%M%S")}'
    os.makedirs(output_path)

    for file in files:
        for rep in range(repetitions):

            subfolder_path = os.path.join(output_path, file.split('\\')[-1].split('.')[0] + "_rep " + str(rep + 1))
            os.mkdir(subfolder_path)

            start_time = time.time()

            print(f'Processing {file} ({rep + 1}/{repetitions})...')
            problem_tuple = parse_problem(dataset, file)
            problem = problem_tuple[0]
            timetable_solver = TimetableSolver(problem, checkpoint_dir=os.path.join(subfolder_path, 'checkpoint'),
                                               graphs_dir=os.path.join(subfolder_path, 'graphs'),
                                               graphs_interval=graph_interval, **ga_params)

            timetable_solver.run()

            stats_file = open(os.path.join(subfolder_path, 'stats.txt'), 'w')

            best_solution, best_cost = timetable_solver.get_best_solution()

            stats_file.write(f'Best solution cost: {best_cost}\n')

            end_time = time.time()
            stats_file.write(f'Execution time: {end_time - start_time} seconds\n')

            stats_file.write(f'Population init time: {timetable_solver.init_population_construction_times}')

            history = timetable_solver.fitness_history
            history.to_csv(os.path.join(subfolder_path, 'history.csv'))

            if dataset == 'itc2007_track3':
                output_itc2007_cb(problem, best_solution, problem_tuple[2], problem_tuple[3],
                                  os.path.join(subfolder_path, 'output.sol'))
            if dataset == 'itc2019':
                ss = RandomStudentSectioning(problem)
                student_classes = ss.apply()
                generate_xml(problem, best_solution, student_classes, os.path.join(subfolder_path, 'output.xml'))

            stats_file.close()


# # random or dfs construction and 1k generations with ls

# In[ ]:


# run_experiment_for_dataset('itc2019',itc2019_files[0:10], 'itc2019(1 of 3) with random construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "random",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})
# 
# run_experiment_for_dataset('itc2019',itc2019_files[0:10] , 'itc2019(1 of 3) with dfs construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "dfs",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})


# In[ ]:


# run_experiment_for_dataset('itc2019',itc2019_files[10:20], 'itc2019(2 of 3) with random construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "random",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})
# 
# run_experiment_for_dataset('itc2019',itc2019_files[10:20] , 'itc2019(2 of 3) with dfs construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "dfs",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})


# In[ ]:


# run_experiment_for_dataset('itc2019',itc2019_files[20:30], 'itc2019(3 of 3) with random construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "random",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})
# 
# run_experiment_for_dataset('itc2019',itc2019_files[20:30] , 'itc2019(3 of 3) with dfs construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "dfs",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})


# In[ ]:


# run_experiment_for_dataset('itc2007_track2',itc2007_track2_files, 'itc2007 track2 with random construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "random",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})
# 
# run_experiment_for_dataset('itc2007_track2',itc2007_track2_files , 'itc2007 track2 with dfs construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "dfs",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})


# In[ ]:


# run_experiment_for_dataset('itc2007_track3',itc2007_track3_files, 'itc2007 track3 with random construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "random",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})
# 
# run_experiment_for_dataset('itc2007_track3',itc2007_track3_files , 'itc2007 track3 with dfs construction and 1k generations with ls', 1, {'population_size': 50, 'no_of_generations': 1000, 'first_population_method': "dfs",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})


# # select datasets only

# In[ ]:


select_2019_datasets = filter_files_by_name(itc2019_files,
                                            ['lums-spr18', 'lums-fal17', 'muni-fi-spr17', 'muni-fi-fal17',
                                             'muni-fsps-spr17'])

select_t2_datasets = filter_files_by_name(itc2007_track2_files, ['comp-2007-2-17'])

select_t3_datasets = filter_files_by_name(itc2007_track3_files,
                                          ['comp18', 'comp01' 'comp11', 'comp12', 'comp03', 'comp15', 'comp14'])

# In[ ]:


# run_experiment_for_dataset('itc2007_track2',select_t2_datasets , 'select itc2007 track 2 with valid dfs construction and 150 generations with ls', 1, {'population_size': 50, 'no_of_generations': 150, 'first_population_method': "dfs",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})


# In[ ]:


# run_experiment_for_dataset('itc2007_track3',select_t3_datasets , 'select itc2007 track 3 with valid dfs construction and 150 generations with ls', 1, {'population_size': 50, 'no_of_generations': 150, 'first_population_method': "dfs",'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,'local_search':True})


# In[ ]:


run_experiment_for_dataset('itc2019', select_2019_datasets[2:3],
                           'select itc2019p1 with valid dfs and 150 generations with ls', 1,
                           {'population_size': 50, 'no_of_generations': 150, 'first_population_method': "dfs",
                            'crossover_chance': 0.7, 'crossover_ratio': 0.5, 'mutation_chance': 0.7,
                            'local_search': True})
