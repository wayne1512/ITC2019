from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class SameRoomDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):
        room_ids = [room_options.id for room_options in rooms_options_chosen]

        violation_count = 0

        for i in range(len(room_ids)):
            for j in range(i + 1, len(room_ids)):
                # assume none of the rooms are null... otherwise why did they add this constraint???
                if room_ids[i] != room_ids[j]:
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):

        not_same_room = [room_option.id != current_room_option.id
                         for room_option in checking_class.room_options]
        mask_sub_part_unflattened[not_same_room, :] = 1
