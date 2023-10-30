from abc import ABC, ABCMeta, abstractmethod

import numpy as np

from models.input.distribution import Distribution


class BaseDistributionHelper(ABC, metaclass=ABCMeta):

    def __init__(self, problem, distribution: Distribution):
        self.problem = problem
        self.distribution = distribution

    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = [self.problem.get_class_by_id(c_id) for c_id in self.distribution.class_ids]
        classes_index = [self.problem.classes.index(c) for c in classes]

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]
        rooms_options_chosen = [c.room_options[rooms_option_chosen_ids[idx]] if len(c.room_options) > 0 else None for
                                c, idx in zip(classes, classes_index)]

        violation_count = self.count_violations(time_options_chosen, rooms_options_chosen)

        if self.distribution.required:
            return violation_count, 0
        return 0, violation_count * self.distribution.penalty

    @abstractmethod
    def count_violations(self, time_options_chosen, rooms_options_chosen):
        pass

    def close_downwards_option(self, solution_search, current_row, current_option, combined_closing_mask):

        current_class = solution_search.classes[current_row]

        if current_class.id not in self.distribution.class_ids:
            return combined_closing_mask

        current_room_option_idx, current_time_option_idx = \
            np.unravel_index(current_option, (max(len(current_class.room_options), 1), len(current_class.time_options)))

        current_time_option = current_class.time_options[current_time_option_idx]
        current_room_option = current_class.room_options[current_room_option_idx] if not \
            solution_search.classesWithoutRooms[current_room_option_idx] >= 0 else None

        for checking_class_id in self.distribution.class_ids:
            checking_class = self.problem.get_class_by_id(checking_class_id)
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            if checking_class_row_index_in_search > current_row:  # only close downwards options
                # not_same_start_time = [time_option.start != current_time_option.start
                #                        for time_option in checking_class.time_options]

                mask_sub_part = combined_closing_mask[checking_class_row_index_in_search,
                                :solution_search.options_per_class[checking_class_row_index_in_search]]
                mask_sub_part_unflattened = mask_sub_part.reshape((-1, len(checking_class.time_options)))
                # mask_sub_part_unflattened[:, not_same_start_time] = 1
                self.close_options_for_checking_class(current_class, current_room_option, current_time_option,
                                                      checking_class, mask_sub_part_unflattened)

    @abstractmethod
    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        pass