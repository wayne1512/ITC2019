import numpy as np


class MaxDayLoadDistributionHelper:

    def __init__(self, problem, distribution, max_load):
        self.problem = problem
        self.distribution = distribution
        self.max_load = max_load

    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = [self.problem.get_class_by_id(c_id) for c_id in self.distribution.class_ids]
        classes_index = [self.problem.classes.index(c) for c in classes]

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]

        day_loads = np.zeros((self.problem.nrWeeks, self.problem.nrDays), dtype=int)

        for time_option in time_options_chosen:
            day_loads[np.outer(time_option.weeks, time_option.days)] = (
                        day_loads[np.outer(time_option.weeks, time_option.days)]
                        + time_option.length)

        extra_load_per_day = np.maximum(day_loads - self.max_load, 0)
        sum_extra_loads = np.sum(extra_load_per_day)

        if self.distribution.required:
            days_with_extra_load = np.count_nonzero(day_loads > self.max_load)
            return days_with_extra_load, 0
        return 0, (sum_extra_loads * self.distribution.penalty) // self.problem.nrWeeks

    def close_downwards_option(self, solution_search, current_row, current_option, combined_closing_mask):
        current_class = solution_search.classes[current_row]

        if current_class.id not in self.distribution.class_ids:
            return

        all_classes = [self.problem.get_class_by_id(class_id) for class_id in self.distribution.class_ids]
        index_of_classes_in_search = [solution_search.classes.index(c) for c in all_classes]
        already_placed_classes = []
        index_of_already_placed_classes_in_search = []
        not_placed_classes = []
        for checking_class_idx, c in zip(index_of_classes_in_search, all_classes):
            if checking_class_idx <= current_row:
                already_placed_classes.append(c)
                index_of_already_placed_classes_in_search.append(checking_class_idx)
            else:
                not_placed_classes.append(c)

        already_placed_time_options = []
        for c, checking_class_idx, in zip(already_placed_classes, index_of_already_placed_classes_in_search):
            selected_option_of_checking_class = np.where(solution_search.decision_table[checking_class_idx] == 1)[0][0]
            room_option_idx, time_option_idx = np.unravel_index(selected_option_of_checking_class, (
                max(len(c.room_options), 1), len(c.time_options)))

            time_option = c.time_options[time_option_idx]
            already_placed_time_options.append(time_option)

        day_loads = np.zeros((self.problem.nrWeeks, self.problem.nrDays), dtype=int)
        for time_option in already_placed_time_options:
            day_loads[np.outer(time_option.weeks, time_option.days)] = day_loads[np.outer(time_option.weeks,
                                                                                          time_option.days)] \
                                                                       + time_option.length

        for checking_class in not_placed_classes:
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            mask_sub_part = combined_closing_mask[checking_class_row_index_in_search,
                            :solution_search.options_per_class[checking_class_row_index_in_search]]
            mask_sub_part_unflattened = mask_sub_part.reshape((-1, len(checking_class.time_options)))

            for checking_time_idx, checking_time_option in enumerate(checking_class.time_options):
                day_loads_copy = day_loads.copy()

                day_loads_copy[checking_time_option.weeks, checking_time_option.days] = (
                        day_loads_copy[checking_time_option.weeks, checking_time_option.days]
                        + checking_time_option.length)

                extra_load_per_day = np.maximum(day_loads_copy - self.max_load, 0)
                sum_extra_loads = np.sum(extra_load_per_day)
                if sum_extra_loads > 0:
                    mask_sub_part_unflattened[:, checking_time_idx] = 1
