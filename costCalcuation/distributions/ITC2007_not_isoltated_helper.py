import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class ITC2007NotIsolatedDistributionHelper(BaseDistributionHelper):

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        pass

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        for time_option in time_options_chosen:

            found_adjacent = False

            for time_option2 in time_options_chosen:
                if (np.all(time_option.days == time_option2.days)
                        and abs(time_option.start - time_option2.start) == 1):
                    found_adjacent = True
                    break

            if not found_adjacent:
                violation_count += 1

        return violation_count

    def close_downwards_option(self, solution_search, current_row, current_option, combined_closing_mask):
        pass
