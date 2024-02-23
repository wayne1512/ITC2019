from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class ITC2007SameRoomDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):
        room_ids = [room_options.id for room_options in rooms_options_chosen]

        violation_count = 0

        # count number of unique room ids
        unique_room_ids_count = len(set(room_ids))

        # if there are more than 1 unique room ids, then there are violations
        return unique_room_ids_count - 1

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        pass
