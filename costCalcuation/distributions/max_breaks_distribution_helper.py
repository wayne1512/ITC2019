import numpy as np


class MaxBreaksDistributionHelper:

    def __init__(self, problem, distribution, max_breaks, break_threshold):
        self.problem = problem
        self.distribution = distribution
        self.max_breaks = max_breaks
        self.break_threshold = break_threshold

    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = [self.problem.get_class_by_id(c_id) for c_id in self.distribution.class_ids]
        classes_index = [self.problem.classes.index(c) for c in classes]

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]

        slots_used = np.full((self.problem.nrWeeks, self.problem.nrDays, self.problem.slotsPerDay), False)

        for time_option in time_options_chosen:
            slots_used[time_option.get_timeslots_mask(self.problem.nrWeeks, self.problem.nrDays,
                                                      self.problem.slotsPerDay)] = True

        violations = 0
        for w in range(self.problem.nrWeeks):
            for d in range(self.problem.nrDays):
                started_day = False
                break_len = 0

                break_count = 0

                for s in slots_used[w, d, :]:
                    if s:
                        started_day = True

                        if break_len >= self.break_threshold + 1:
                            break_count += 1

                        break_len = 0
                    elif started_day:
                        break_len += 1

                violations += max(break_count - self.max_breaks, 0)

        if self.distribution.required:
            return violations, 0
        return 0, (violations * self.distribution.penalty) // self.problem.nrWeeks

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
            selected_option_of_checking_class = np.where(solution_search.decisionTable[checking_class_idx] == 1)[0][0]
            room_option_idx, time_option_idx = np.unravel_index(selected_option_of_checking_class, (
                max(len(c.room_options), 1), len(c.time_options)))

            time_option = c.time_options[time_option_idx]
            already_placed_time_options.append(time_option)

        slots_used = np.full((self.problem.nrWeeks, self.problem.nrDays, self.problem.slotsPerDay), False)

        for time_option in already_placed_time_options:
            slots_used[time_option.get_timeslots_mask(self.problem.nrWeeks, self.problem.nrDays,
                                                      self.problem.slotsPerDay)] = True

        for checking_class in not_placed_classes:
            checking_class_row_index_in_search = solution_search.classes.index(checking_class)

            mask_sub_part = combined_closing_mask[checking_class_row_index_in_search,
                            :solution_search.options_per_class[checking_class_row_index_in_search]]
            mask_sub_part_unflattened = mask_sub_part.reshape((-1, len(checking_class.time_options)))

            for checking_time_idx, checking_time_option in enumerate(checking_class.time_options):
                slots_used_copy = slots_used.copy()

                slots_used_copy[checking_time_option.get_timeslots_mask(self.problem.nrWeeks, self.problem.nrDays,
                                                                   self.problem.slotsPerDay)] = True

                for w in range(self.problem.nrWeeks):
                    if checking_time_option.weeks[w]:
                        for d in range(self.problem.nrDays):
                            if checking_time_option.days[d]:
                                started_day = False
                                break_len = 0

                                break_count = 0

                                for s in slots_used_copy[w, d, :]:
                                    if s:
                                        started_day = True

                                        if break_len >= self.break_threshold + 1:
                                            mask_sub_part_unflattened[:, checking_time_idx] = 1

                                        break_len = 0
                                    elif started_day:
                                        break_len += 1
