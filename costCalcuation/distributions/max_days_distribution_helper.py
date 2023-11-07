import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class MaxDaysDistributionHelper(BaseDistributionHelper):

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        pass

    def __init__(self, problem, distribution: Distribution, max_Days):
        super().__init__(problem, distribution)
        self.max_days = max_Days

    def count_violations(self, time_options_chosen, rooms_options_chosen):
        days = [time_option.days for time_option in time_options_chosen]
        days_merged = np.logical_or.reduce(days)

        day_count = np.count_nonzero(days_merged)

        violation_count = day_count - self.max_days if day_count > self.max_days else 0

        return violation_count

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
            selected_option_of_checking_class = np.where(solution_search.decisionTable[checking_class_idx] == 1)[0][0]
            room_option_idx, time_option_idx = np.unravel_index(selected_option_of_checking_class, (
                max(len(c.room_options), 1), len(c.time_options)))

            time_option = c.time_options[time_option_idx]
            already_placed_time_options.append(time_option)

        already_placed_days = np.logical_or.reduce([t.days for t in already_placed_time_options])
        for checking_class in not_placed_classes:
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            mask_sub_part = combined_closing_mask[checking_class_row_index_in_search,
                            :solution_search.options_per_class[checking_class_row_index_in_search]]
            mask_sub_part_unflattened = mask_sub_part.reshape((-1, len(checking_class.time_options)))

            for checking_time_idx, checking_time_option in enumerate(checking_class.time_options):
                if np.count_nonzero(
                        np.logical_or.reduce([already_placed_days, checking_time_option.days])) > self.max_days:
                    mask_sub_part_unflattened[:, checking_time_idx] = 1
