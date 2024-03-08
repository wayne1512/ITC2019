import numpy as np


class MaxBlockDistributionHelper:

    def __init__(self, problem, distribution, max_len, break_threshold):
        self.problem = problem
        self.distribution = distribution
        self.max_len = max_len
        self.break_threshold = break_threshold

    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = [self.problem.get_class_by_id(c_id) for c_id in self.distribution.class_ids]
        classes_index = [self.problem.classes.index(c) for c in classes]

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]

        slots_used = np.full((self.problem.nrWeeks, self.problem.nrDays, self.problem.slotsPerDay), -1)

        for i, time_option in enumerate(time_options_chosen):
            slots_used[time_option.get_timeslots_mask(self.problem.nrWeeks, self.problem.nrDays,
                                                      self.problem.slotsPerDay)] = i

        violations = []
        for w in range(self.problem.nrWeeks):
            for d in range(self.problem.nrDays):
                in_block = False
                break_len = 0
                block_start = 0
                last_slot_used_in_block = 0

                for si, s in enumerate(slots_used[w, d, :]):

                    if s >= 0:

                        if not in_block:
                            break_len = 0
                            in_block = True
                            block_start = si

                        last_slot_used_in_block = si
                    elif in_block:
                        break_len += 1
                        if break_len >= self.break_threshold + 1:
                            in_block = False

                            if (last_slot_used_in_block - block_start > self.max_len and  # not 1 class
                                    slots_used[w, d, block_start] != slots_used[w, d, last_slot_used_in_block]):
                                violations.append((w, d, block_start, last_slot_used_in_block))
                if in_block:
                    if (last_slot_used_in_block - block_start > self.max_len and  # not 1 class
                            slots_used[w, d, block_start] != slots_used[w, d, last_slot_used_in_block]):
                        violations.append((w, d, block_start, last_slot_used_in_block))

        violations_count = len(violations)

        if self.distribution.required:
            return violations_count, 0
        return 0, (violations_count * self.distribution.penalty) // self.problem.nrWeeks

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

        slots_used = np.full((self.problem.nrWeeks, self.problem.nrDays, self.problem.slotsPerDay), -1)

        for i, time_option in enumerate(already_placed_time_options):
            slots_used[time_option.get_timeslots_mask(self.problem.nrWeeks, self.problem.nrDays,
                                                      self.problem.slotsPerDay)] = i

        for checking_class in not_placed_classes:
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            mask_sub_part = combined_closing_mask[checking_class_row_index_in_search,
                            :solution_search.options_per_class[checking_class_row_index_in_search]]
            mask_sub_part_unflattened = mask_sub_part.reshape((-1, len(checking_class.time_options)))

            for checking_time_idx, checking_time_option in enumerate(checking_class.time_options):
                slots_used_copy = np.copy(slots_used)

                slots_used_copy[checking_time_option.get_timeslots_mask(self.problem.nrWeeks, self.problem.nrDays,
                                                                        self.problem.slotsPerDay)] = len(
                    already_placed_time_options)

                for w in range(self.problem.nrWeeks):
                    if checking_time_option.weeks[w]:
                        for d in range(self.problem.nrDays):
                            if checking_time_option.weeks[d]:

                                in_block = False
                                break_len = 0
                                block_start = 0
                                last_slot_used_in_block = 0

                                for si, s in enumerate(slots_used_copy[w, d, :]):

                                    if s >= 0:

                                        if not in_block:
                                            break_len = 0
                                            in_block = True
                                            block_start = si

                                        break_len = 0
                                        last_slot_used_in_block = si
                                    elif in_block:
                                        break_len += 1
                                        if break_len >= self.break_threshold + 1:
                                            in_block = False

                                            if (last_slot_used_in_block - block_start > self.max_len and  # not 1 class
                                                    slots_used_copy[w, d, block_start] !=
                                                    slots_used_copy[w, d, last_slot_used_in_block]):
                                                mask_sub_part_unflattened[:, checking_time_idx] = 1
                                if in_block:
                                    if (last_slot_used_in_block - block_start > self.max_len and  # not 1 class
                                            slots_used_copy[w, d, block_start] != slots_used_copy[
                                                w, d, last_slot_used_in_block]):
                                        mask_sub_part_unflattened[:, checking_time_idx] = 1
