import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper


class PrecedenceDistributionHelper(BaseDistributionHelper):
    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        for i in range(len(time_options_chosen)):

            earlier_class_first_meeting = (
                np.nonzero(time_options_chosen[i].weeks)[0][0],
                np.nonzero(time_options_chosen[i].days)[0][0],
                time_options_chosen[i].start + time_options_chosen[i].length
            )

            for j in range(i + 1, len(time_options_chosen)):
                later_class_first_meeting = (
                    np.nonzero(time_options_chosen[j].weeks)[0][0],
                    np.nonzero(time_options_chosen[j].days)[0][0],
                    time_options_chosen[j].start
                )

                if later_class_first_meeting < earlier_class_first_meeting:
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        not_preceding = []
        for time_option in checking_class.time_options:

            if self.distribution.class_ids.index(current_class.id) < self.distribution.class_ids.index(
                    checking_class.id):
                earlier_time_option, later_time_option = current_time_option, time_option
            else:
                later_time_option, earlier_time_option = current_time_option, time_option

            earlier_class_first_meeting = (
                np.nonzero(earlier_time_option.weeks)[0][0],
                np.nonzero(earlier_time_option.days)[0][0],
                earlier_time_option.start + earlier_time_option.length
            )

            later_class_first_meeting = (
                np.nonzero(later_time_option.weeks)[0][0],
                np.nonzero(later_time_option.days)[0][0],
                later_time_option.start
            )

            not_preceding.append(
                later_class_first_meeting < earlier_class_first_meeting
            )
        mask_sub_part_unflattened[:, not_preceding] = 1
