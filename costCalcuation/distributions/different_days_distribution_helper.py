import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class DifferentDaysDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):
        days = [time_option.days for time_option in time_options_chosen]

        violation_count = 0

        for i in range(len(days)):
            for j in range(i + 1, len(days)):

                if np.any(np.logical_and(days[i], days[j])):
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        not_different_days = [np.any(np.logical_and(time_option.days, current_time_option.days)) for time_option in
                              checking_class.time_options]
        mask_sub_part_unflattened[:, not_different_days] = 1
