import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper, get_room_and_time_chosen


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

    def check_ac4_constraints(self, ac4, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
        time_i = get_room_and_time_chosen(ac4.solution_search, class_row_i, class_row_i_option)[1]
        time_j = get_room_and_time_chosen(ac4.solution_search, class_row_j, class_row_j_option)[1]

        i_id = ac4.solution_search.classes[class_row_i].id
        j_id = ac4.solution_search.classes[class_row_j].id

        earlier_time, later_time = (time_i, time_j) \
            if self.distribution.class_ids.index(i_id) < self.distribution.class_ids.index(j_id) \
            else (time_j, time_i)

        earlier_class_first_meeting = (
            np.nonzero(earlier_time.weeks)[0][0],
            np.nonzero(earlier_time.days)[0][0],
            earlier_time.start + earlier_time.length
        )

        later_class_first_meeting = (
            np.nonzero(later_time.weeks)[0][0],
            np.nonzero(later_time.days)[0][0],
            later_time.start
        )

        return later_class_first_meeting >= earlier_class_first_meeting
