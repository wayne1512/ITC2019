import numpy as np


class DoubleBookingHelper:

    def __init__(self, problem):
        self.problem = problem

    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        for i in range(len(time_options_chosen)):
            i_room_option = rooms_options_chosen[i]
            i_room_id = i_room_option.id if i_room_option is not None else None
            for j in range(i + 1, len(time_options_chosen)):

                j_room_option = rooms_options_chosen[j]
                j_room_id = j_room_option.id if j_room_option is not None else None

                if not (
                        i_room_option is None
                        or j_room_option is None
                        or i_room_id != j_room_id
                        or
                        (time_options_chosen[j].start + time_options_chosen[j].length) <= time_options_chosen[i].start
                        or
                        (time_options_chosen[i].start + time_options_chosen[i].length) <= time_options_chosen[j].start
                        or not np.any(np.logical_and(time_options_chosen[i].days, time_options_chosen[j].days))
                        or not np.any(np.logical_and(time_options_chosen[i].weeks, time_options_chosen[j].weeks))

                ):
                    violation_count += 1

        return violation_count, 0

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        current_room_id = current_room_option.id if current_room_option is not None else None

        room_options_or_equivalent = checking_class.room_options
        if len(room_options_or_equivalent) == 0:
            room_options_or_equivalent = [None]  # if empty replace with array of [None] so that loop executes once

        for room_option_index, room_option in enumerate(room_options_or_equivalent):

            room_id = room_option.id if room_option is not None else 0

            for time_option_index, time_option in enumerate(checking_class.time_options):
                if not (
                        room_option is None
                        or current_room_option is None
                        or current_room_id != room_id
                        or (time_option.start + time_option.length) <= current_time_option.start
                        or
                        (current_time_option.start + current_time_option.length) <= time_option.start
                        or not np.any(np.logical_and(current_time_option.days, time_option.days))
                        or not np.any(np.logical_and(current_time_option.weeks, time_option.weeks))

                ):
                    mask_sub_part_unflattened[room_option_index, time_option_index] = 1

    def close_downwards_option(self, solution_search, current_row, current_option, combined_closing_mask):
        # todo move to common base class (careful of changes)
        current_class = solution_search.classes[current_row]

        current_room_option_idx, current_time_option_idx = \
            np.unravel_index(current_option, (max(len(current_class.room_options), 1), len(current_class.time_options)))

        current_time_option = current_class.time_options[current_time_option_idx]
        current_room_option = current_class.room_options[current_room_option_idx] if not \
            solution_search.classes_without_rooms[current_row] else None

        for checking_class in self.problem.classes:
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            if checking_class_row_index_in_search > current_row:  # only close downwards options

                mask_sub_part = combined_closing_mask[checking_class_row_index_in_search,
                                :solution_search.options_per_class[checking_class_row_index_in_search]]
                mask_sub_part_unflattened = mask_sub_part.reshape((-1, len(checking_class.time_options)))
                self.close_options_for_checking_class(current_class, current_room_option, current_time_option,
                                                      checking_class, mask_sub_part_unflattened)
