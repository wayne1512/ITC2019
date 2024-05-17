import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


# used for SC3 of ITC2007 PE
class ITC2007MaxConsecutiveDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution, limit):
        self.limit = limit
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        slots_used = np.full((self.problem.nrDays, self.problem.slotsPerDay), -1)

        for i, time_option in enumerate(time_options_chosen):
            slots_used[time_option.days, time_option.start] = i

        for day in range(self.problem.nrDays):
            for slot in range(self.problem.slotsPerDay):

                consecutive_slots = 0

                if slots_used[day, slot] != -1:
                    consecutive_slots += 1
                else:
                    consecutive_slots = 0

                if consecutive_slots > self.limit:
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        pass
