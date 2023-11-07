from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class SameStartDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):
        start_times = [time_option.start for time_option in time_options_chosen]

        violation_count = 0

        for i in range(len(start_times)):
            for j in range(i + 1, len(start_times)):
                if start_times[i] != start_times[j]:
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        not_same_start_time = [time_option.start != current_time_option.start
                               for time_option in checking_class.time_options]
        mask_sub_part_unflattened[:, not_same_start_time] = 1
