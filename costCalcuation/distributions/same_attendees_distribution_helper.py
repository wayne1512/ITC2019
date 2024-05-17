import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper, get_room_and_time_chosen
from models.input.distribution import Distribution


class SameAttendeesDistributionHelper(BaseDistributionHelper):

    def __init__(self, problem, distribution: Distribution):
        super().__init__(problem, distribution)

    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        for i in range(len(time_options_chosen)):
            for j in range(i + 1, len(time_options_chosen)):
                i_room_option = rooms_options_chosen[i]
                i_room_id = i_room_option.id if i_room_option is not None else None
                j_room_option = rooms_options_chosen[j]
                j_room_id = j_room_option.id if j_room_option is not None else None

                travel_time = self.problem.get_travel_time(i_room_id, j_room_id) \
                    if i_room_option is not None and j_room_option is not None else 0
                if not (
                        (time_options_chosen[j].start + time_options_chosen[j].length +
                         travel_time) <= time_options_chosen[i].start
                        or
                        (time_options_chosen[i].start + time_options_chosen[i].length +
                         travel_time) <= time_options_chosen[j].start
                        or not np.any(np.logical_and(time_options_chosen[i].days, time_options_chosen[j].days))
                        or not np.any(np.logical_and(time_options_chosen[i].weeks, time_options_chosen[j].weeks))

                ):
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        unfeasible = []

        current_room_id = current_room_option.id if current_room_option is not None else None

        room_options_or_equivalent = checking_class.room_options
        if len(room_options_or_equivalent) == 0:
            room_options_or_equivalent = [None]  # if empty replace with array of [None] so that loop executes once

        for room_option in room_options_or_equivalent:

            unfeasible_in_current_room = []

            room_id = room_option.id if room_option is not None else 0

            travel = self.problem.get_travel_time(room_id,
                                                  current_room_id) if current_room_option is not None and room_option is not None else 0
            for time_option in checking_class.time_options:
                unfeasible_in_current_room.append(
                    not (
                            (time_option.start + time_option.length + travel) <= current_time_option.start
                            or
                            (current_time_option.start + current_time_option.length + travel) <= time_option.start
                            or not np.any(np.logical_and(current_time_option.days, time_option.days))
                            or not np.any(np.logical_and(current_time_option.weeks, time_option.weeks))

                    )
                )
            unfeasible.append(unfeasible_in_current_room)
        mask_sub_part_unflattened[unfeasible] = 1

    def check_ac4_constraints(self, ac4, class_row_i, class_row_j, class_row_i_option, class_row_j_option):
        room_i, time_i = get_room_and_time_chosen(ac4.solution_search, class_row_i, class_row_i_option)
        room_j, time_j = get_room_and_time_chosen(ac4.solution_search, class_row_j, class_row_j_option)

        start_i = time_i.start
        end_i = time_i.start + time_i.length
        start_j = time_j.start
        end_j = time_j.start + time_j.length

        min_gap = self.problem.get_travel_time(room_i.id, room_j.id) if room_i is not None and room_j is not None else 0

        return (
                not np.any(np.logical_and(time_i.days, time_j.days))
                or not np.any(np.logical_and(time_i.weeks, time_j.weeks))
                or (end_i + min_gap) <= start_j
                or (end_j + min_gap) <= start_i
        )
