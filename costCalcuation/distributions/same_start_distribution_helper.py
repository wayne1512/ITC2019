import numpy as np

from models.input.distribution import Distribution


class SameStartDistributionHelper:

    def __init__(self, problem, distribution: Distribution):
        self.problem = problem
        self.distribution = distribution

    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = [self.problem.get_class_by_id(c_id) for c_id in self.distribution.class_ids]
        classes_index = [self.problem.classes.index(c) for c in classes]

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]

        start_times = [time_option.start for time_option in time_options_chosen]

        violation_count = 0

        for i in range(len(start_times)):
            for j in range(i + 1, len(start_times)):
                if start_times[i] != start_times[j]:
                    violation_count += 1

        if self.distribution.required:
            return violation_count, 0
        return 0, violation_count * self.distribution.penalty

    def close_downwards_option(self, solution_search, current_row, current_option):

        combined_closing_mask = np.full_like(solution_search.decisionTable, False, dtype=bool)

        current_class = solution_search.classes[current_row]

        if current_class.id not in self.distribution.class_ids:
            return combined_closing_mask

        current_class_row = solution_search.decisionTable[current_row]

        current_class_options_unflattened = current_class_row[:solution_search.options_per_class[current_row]].reshape(
            (-1, len(current_class.time_options)))

        current_room_option_idx, current_time_option_idx = \
            np.unravel_index(current_option, current_class_options_unflattened.shape)

        current_time_option = current_class.time_options[current_time_option_idx]

        for checking_class_id in self.distribution.class_ids:
            checking_class = self.problem.get_class_by_id(checking_class_id)
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            if checking_class_row_index_in_search > current_row:  # only close downwards options
                not_same_start_time = [time_option.start != current_time_option.start
                                       for time_option in checking_class.time_options]

                checking_class_row = solution_search.decisionTable[checking_class_row_index_in_search]
                checking_class_option_unflattened = checking_class_row[
                                                    :solution_search.options_per_class[
                                                        checking_class_row_index_in_search]].reshape(
                    (-1, len(checking_class.time_options)))

                mask = np.full(checking_class_option_unflattened.shape, False)
                mask[:, not_same_start_time] = 1
                mask_flat = mask.flat

                mask_padded = np.full(combined_closing_mask.shape[1], False)
                mask_padded[:len(mask_flat)] = mask_flat

                combined_closing_mask[checking_class_row_index_in_search] = mask_padded
        return combined_closing_mask
