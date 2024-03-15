import os

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from ac4 import AC4
from depth_first_search_solver import DepthFirstSearchSolver
from parse_input import parse_xml
from solution_search import SolutionSearch


@pytest.fixture()
def problem_dir():
    return os.path.join(os.path.dirname(__file__), "distribution_test_problems")


@pytest.mark.parametrize("problem_file_name, expected_gene", [
    ("sameStart.xml", [[-1, 0], [-1, 1]]),
    ("sameTimeEqualLength.xml", [[-1, 0], [-1, 2]]),
    ("sameTimeDiffLength.xml", [[-1, 0], [-1, 2]]),
    ("differentTime.xml", [[-1, 0], [-1, 3]]),
    ("sameDays.xml", [[-1, 0], [-1, 1]]),
    ("differentDays.xml", [[-1, 0], [-1, 2]]),
    ("sameWeeks.xml", [[-1, 0], [-1, 1]]),
    ("differentWeeks.xml", [[-1, 0], [-1, 2]]),
    ("overlap.xml", [[-1, 0], [-1, 4]]),
    ("notOverlap.xml", [[-1, 0], [-1, 1]]),
    ("sameAttendees.xml", [[0, 0], [0, 3]]),
    ("sameRoom.xml", [[0, 0], [1, 0]]),
    ("differentRoom.xml", [[0, 0], [1, 0]]),
    ("precedenceByWeek.xml", [[-1, 0], [-1, 1]]),
    ("precedenceByWeekReversed.xml", [[-1, 0], [-1, 1]]),
    ("workday.xml", [[-1, 0], [-1, 2]]),
    ("WorkdayWithHugeLesson.xml", [[-1, 0], [-1, 2]]),
    ("minGap.xml", [[-1, 0], [-1, 2]]),
    ("maxDays.xml", [[-1, 0], [-1, 2]]),
    ("maxDayLoad.xml", [[-1, 0], [-1, 1]]),
    ("maxBreaks.xml", [[-1, 0], [-1, 0], [-1, 2]]),
    ("maxBlock.xml", [[-1, 0], [-1, 0], [-1, 1]]),
    ("doubleBooking.xml", [[0, 0], [0, 1]]),
])
def test_depth_first_solver(problem_dir, problem_file_name, expected_gene):
    path = os.path.join(problem_dir, problem_file_name)

    test_problem = parse_xml(path)[0]

    search = SolutionSearch(test_problem)
    solver = DepthFirstSearchSolver(search)
    solver.solve()

    actual_gene = search.get_result_as_gene()

    assert_array_equal(actual_gene, expected_gene)


@pytest.mark.parametrize("problem_file_name, expected_gene", [
    ("sameStart.xml", [[-1, 0], [-1, 1]]),
    ("sameTimeEqualLength.xml", [[-1, 0], [-1, 2]]),
    ("sameTimeDiffLength.xml", [[-1, 0], [-1, 2]]),
    ("differentTime.xml", [[-1, 0], [-1, 3]]),
    ("sameDays.xml", [[-1, 0], [-1, 1]]),
    ("differentDays.xml", [[-1, 0], [-1, 2]]),
    ("sameWeeks.xml", [[-1, 0], [-1, 1]]),
    ("differentWeeks.xml", [[-1, 0], [-1, 2]]),
    ("overlap.xml", [[-1, 0], [-1, 4]]),
    ("notOverlap.xml", [[-1, 0], [-1, 1]]),
    ("sameAttendees.xml", [[0, 0], [0, 3]]),
    ("sameRoom.xml", [[0, 0], [1, 0]]),
    ("differentRoom.xml", [[0, 0], [1, 0]]),
    ("precedenceByWeek.xml", [[-1, 0], [-1, 1]]),
    ("precedenceByWeekReversed.xml", [[-1, 0], [-1, 1]]),
    # ("workday.xml", [[-1, 0], [-1, 2]]),
    # ("WorkdayWithHugeLesson.xml", [[-1, 0], [-1, 2]]),
    ("minGap.xml", [[-1, 0], [-1, 2]]),
    # ("maxDays.xml", [[-1, 0], [-1, 2]]),
    # ("maxDayLoad.xml", [[-1, 0], [-1, 1]]),
    # ("maxBreaks.xml", [[-1, 0], [-1, 0], [-1, 2]]),
    # ("maxBlock.xml", [[-1, 0], [-1, 0], [-1, 1]]),
    ("doubleBooking.xml", [[0, 0], [0, 1]]),
])
def test_ac4(problem_dir, problem_file_name, expected_gene):
    path = os.path.join(problem_dir, problem_file_name)

    test_problem = parse_xml(path)[0]

    search = SolutionSearch(test_problem)

    ac4 = AC4(search)
    ac4.apply()

    # count 0s in each row to get open options for each class
    open_options = np.count_nonzero(search.decision_table == 0, axis=1)

    if np.any(open_options > 1):
        raise ValueError("AC4 did not close all options")

    if np.any(open_options < 1):
        raise ValueError("AC4 closed too many options")

    search.decision_table[search.decision_table == 0] = 1
    actual_gene = search.get_result_as_gene()
    assert_array_equal(actual_gene, expected_gene)
