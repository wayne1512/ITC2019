import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class ITC2007MinDaysDistributionHelper(BaseDistributionHelper):

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        pass

    def __init__(self, problem, distribution: Distribution, min_days):
        super().__init__(problem, distribution)
        self.min_days = min_days

    def count_violations(self, time_options_chosen, rooms_options_chosen):
        days = [time_option.days for time_option in time_options_chosen]
        days_merged = np.logical_or.reduce(days)

        day_count = np.count_nonzero(days_merged)

        violation_count = self.min_days - day_count if day_count < self.min_days else 0

        return violation_count

    def close_downwards_option(self, solution_search, current_row, current_option, combined_closing_mask):
        pass
