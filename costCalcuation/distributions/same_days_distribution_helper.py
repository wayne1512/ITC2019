import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper, get_room_and_time_chosen
from models.input.distribution import Distribution


class SameDaysDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):
        days = [time_option.days for time_option in time_options_chosen]

        violation_count = 0

        for i in range(len(days)):
            for j in range(i + 1, len(days)):
                days_or = np.logical_or(days[i], days[j])

                if not (np.array_equal(days_or, days[i]) or np.array_equal(days_or, days[j])):
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        not_same_days = []
        for time_option in checking_class.time_options:
            days_or = np.logical_or(current_time_option.days, time_option.days)
            not_same_days.append(
                not (np.array_equal(days_or, current_time_option.days) or np.array_equal(days_or, time_option.days))
            )
        mask_sub_part_unflattened[:, not_same_days] = 1

    def check_ac4_constraints(self, ac4, class_row_i, class_row_j, class_row_i_option, class_row_j_option):

        days_i = get_room_and_time_chosen(ac4.solution_search, class_row_i, class_row_i_option)[1].days
        days_j = get_room_and_time_chosen(ac4.solution_search, class_row_j, class_row_j_option)[1].days

        days_or = np.logical_or(days_i, days_j)

        return np.array_equal(days_or, days_i) or np.array_equal(days_or, days_j)
