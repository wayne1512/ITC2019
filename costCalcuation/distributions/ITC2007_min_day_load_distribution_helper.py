import numpy as np


class ITC2007MinDayLoadDistributionHelper:

    def __init__(self, problem, distribution, min_load):
        self.problem = problem
        self.distribution = distribution
        self.min_load = min_load

    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = [self.problem.get_class_by_id(c_id) for c_id in self.distribution.class_ids]
        classes_index = [self.problem.classes.index(c) for c in classes]

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]

        day_loads = np.zeros(self.problem.nrDays, dtype=int)

        for time_option in time_options_chosen:
            day_loads[time_option.days] += 1

        days_with_too_few_events = np.count_nonzero(
            np.logical_and(np.greater(day_loads, 0), np.less(day_loads, self.min_load)))

        if self.distribution.required:
            return days_with_too_few_events, 0
        return 0, days_with_too_few_events * self.distribution.penalty

    def close_downwards_option(self, solution_search, current_row, current_option, combined_closing_mask):
        pass
