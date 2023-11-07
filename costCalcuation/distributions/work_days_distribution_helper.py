import numpy as np

from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper
from models.input.distribution import Distribution


class WorkDaysDistributionHelper(BaseDistributionHelper):

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        pass  # not needed

    def __init__(self, problem, distribution: Distribution, maxTimeSlots):
        super().__init__(problem, distribution)
        self.maxTimeSlots = maxTimeSlots

    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        for i in range(len(time_options_chosen)):
            for j in range(i + 1, len(time_options_chosen)):
                if not (
                        not np.any(np.logical_and(time_options_chosen[i].days, time_options_chosen[j].days))
                        or not np.any(np.logical_and(time_options_chosen[i].weeks, time_options_chosen[j].weeks))
                        or (max(time_options_chosen[i].start + time_options_chosen[i].length,
                                time_options_chosen[j].start + time_options_chosen[j].length)
                            - min(time_options_chosen[i].start, time_options_chosen[j].start))
                        <= self.maxTimeSlots

                ):
                    violation_count += 1

        return violation_count

    def close_downwards_option(self, solution_search, current_row, current_option, combined_closing_mask):
        current_class = solution_search.classes[current_row]

        if current_class.id not in self.distribution.class_ids:
            return

        all_classes = [self.problem.get_class_by_id(class_id) for class_id in self.distribution.class_ids]
        index_of_classes_in_search = [solution_search.classes.index(c) for c in all_classes]
        already_placed_classes = []
        index_of_already_placed_classes_in_search = []
        not_placed_classes = []
        for checking_class_idx, c in zip(index_of_classes_in_search, all_classes):
            if checking_class_idx <= current_row:
                already_placed_classes.append(c)
                index_of_already_placed_classes_in_search.append(checking_class_idx)
            else:
                not_placed_classes.append(c)

        already_placed_time_options = []
        for c, checking_class_idx, in zip(already_placed_classes, index_of_already_placed_classes_in_search):
            selected_option_of_checking_class = np.where(solution_search.decision_table[checking_class_idx] == 1)[0][0]
            room_option_idx, time_option_idx = np.unravel_index(selected_option_of_checking_class, (
                max(len(c.room_options), 1), len(c.time_options)))

            time_option = c.time_options[time_option_idx]
            already_placed_time_options.append(time_option)

        min_and_max_slot_for_each_day = np.full((self.problem.nrWeeks, self.problem.nrDays, 2), -1)
        min_slot_for_each_day = min_and_max_slot_for_each_day[:, :, 0]
        min_slot_for_each_day[:] = self.problem.slotsPerDay
        max_slot_for_each_day = min_and_max_slot_for_each_day[:, :, 1]
        max_slot_for_each_day[:] = -1

        for time_option in already_placed_time_options:
            start = time_option.start
            end = time_option.start + time_option.length

            min_slot_for_each_day[time_option.weeks, time_option.days] = np.where(
                min_slot_for_each_day[time_option.weeks, time_option.days] <= start,
                min_slot_for_each_day[time_option.weeks, time_option.days], start)

            max_slot_for_each_day[time_option.weeks, time_option.days] = np.where(
                max_slot_for_each_day[time_option.weeks, time_option.days] >= end,
                max_slot_for_each_day[time_option.weeks, time_option.days], end)

        for checking_class in not_placed_classes:
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            mask_sub_part = combined_closing_mask[checking_class_row_index_in_search,
                            :solution_search.options_per_class[checking_class_row_index_in_search]]
            mask_sub_part_unflattened = mask_sub_part.reshape((-1, len(checking_class.time_options)))

            for checking_time_idx, checking_time_option in enumerate(checking_class.time_options):
                min_copy = np.copy(min_slot_for_each_day)
                max_copy = np.copy(max_slot_for_each_day)

                min_copy[checking_time_option.weeks, checking_time_option.days] = np.where(
                    min_copy[checking_time_option.weeks, checking_time_option.days] <= checking_time_option.start,
                    min_copy[checking_time_option.weeks, checking_time_option.days], checking_time_option.start)

                max_copy[checking_time_option.weeks, checking_time_option.days] = np.where(
                    max_copy[
                        checking_time_option.weeks, checking_time_option.days] >=
                    checking_time_option.start + checking_time_option.length,
                    max_copy[checking_time_option.weeks, checking_time_option.days],
                    checking_time_option.start + checking_time_option.length)

                # ignore min and max values for days were no relevant classes are held
                min_copy[min_copy == self.problem.slotsPerDay] = 0
                max_copy[max_copy == -1] = 0

                work_day = max_copy - min_copy
                violated_max_work_day = np.max(work_day) > self.maxTimeSlots

                if violated_max_work_day:
                    mask_sub_part_unflattened[:, checking_time_idx] = 1
