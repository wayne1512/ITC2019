# Code for "A Metaheuristic approach to the University course timetabling problem"

## Quick start

'parse_input.py' contains functions to parse the input data from the .txt files in the 'data' folder. The 'data' folder
contains the input data from the ITC2007 track2, ITC2007 track3 and ITC2019 datasets.

'timetable_solver'.py contains the main implementation of the algorithm.

'solution_to_xml.py' contains functions to convert the output of the algorithm to the output format required by the
ITC2007 and ITC2019 datasets.

### Test Scripts

The scripts used for the experiments are in the files 'stage 1 runner.ipynb' and 'stage 2 runner.ipynb'. The first file
was used to test the different techniques for the 1st stage (constructing the initial population) and the second file
was used to test the entire process including the generation of intial population, different GAs (GA+LS,GA+ILS, and
GSGA) and student sectioning for the ITC2019 datasets.

These jupyter notebooks were used as a common base for the experiments, and although they serve as a good demonstration
on running the algorithm, they are not necessary to run the algorithm.

## Other files

'experiment_analysis' folder contained the notebooks required to analyze the results of the experiments.
depth_first_search_analysis.ipynb' and 'stage2_analysis.ipynb' contain the code used to analyze the results of the
experiments run from the runners described above.

'genetic_operators' folder contain the functions for the genetic operators used in the algorithm such as crossovers,
mutation, LS, ILS, and tournament selection.

'costCalculation' folder contains the distribution helpers which provide implementation of common operations for each
type of distribution including calculating costs and closing options during the Forward Checking process during the
generation of the initial population.

