import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper, get_room_and_time_chosen
from models.input.distribution import Distribution


class OverlapDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        for i in range(len(time_options_chosen)):
            for j in range(i + 1, len(time_options_chosen)):
                if not (
                        time_options_chosen[i].start < (time_options_chosen[j].start + time_options_chosen[j].length)
                        and
                        time_options_chosen[j].start < (time_options_chosen[i].start + time_options_chosen[i].length)
                        and np.any(np.logical_and(time_options_chosen[i].days, time_options_chosen[j].days))
                        and np.any(np.logical_and(time_options_chosen[i].weeks, time_options_chosen[j].weeks))

                ):
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        not_overlap = []
        for time_option in checking_class.time_options:
            not_overlap.append(
                not (
                        current_time_option.start < (time_option.start + time_option.length)
                        and
                        time_option.start < (current_time_option.start + current_time_option.length)
                        and np.any(np.logical_and(current_time_option.days, time_option.days))
                        and np.any(np.logical_and(current_time_option.weeks, time_option.weeks))

                )
            )
        mask_sub_part_unflattened[:, not_overlap] = 1

    def check_ac4_constraints(self, ac4, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
        time_i = get_room_and_time_chosen(ac4.solution_search, class_row_i, class_row_i_option)[1]
        time_j = get_room_and_time_chosen(ac4.solution_search, class_row_j, class_row_j_option)[1]

        return (
                time_i.start < (time_j.start + time_j.length)
                and
                time_j.start < (time_i.start + time_i.length)
                and np.any(np.logical_and(time_i.days, time_j.days))
                and np.any(np.logical_and(time_i.weeks, time_j.weeks))
        )
