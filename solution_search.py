import numpy as np

from models.input.problem import Problem


class SolutionSearch:
    def __init__(self, problem: Problem):
        self.options_per_class = None
        self.classesWithoutRooms = None
        self.decisionTable = None

        self.classes = problem.classes.copy()
        self.problem = problem

        self.setup_decision_table()

    def setup_decision_table(self):
        self.get_options_per_class()

        self.decisionTable = np.full((len(self.classes), max(self.options_per_class)), -1)

        for i, c in enumerate(self.options_per_class):
            self.decisionTable[i, :c] = 0
            checking_class = self.classes[i]

            # close unavailable rooms
            unflattened_class_choices = self.decisionTable[i][
                                        :c].reshape(
                (-1, len(self.classes[i].time_options)))

            for room_option_idx, room_id in enumerate(checking_class.room_options_ids):
                room = list(filter(lambda r: r.id == room_id, self.problem.rooms))[0]

                # list of time options, True if room is unavailable at this time
                time_mask = [self.is_room_unavailable_during_timeslot(room, time_option) for time_option in
                             checking_class.time_options]

                unflattened_class_choices[room_option_idx, :][time_mask] = -1

    def is_room_unavailable_during_timeslot(self, room, time_option):
        time_option_timeslots = time_option.get_timeslots_mask(self.problem.nrWeeks,
                                                               self.problem.nrDays,
                                                               self.problem.slotsPerDay)
        for unavailability in room.unavailabilities:
            unavailability_timeslots = unavailability.get_timeslots_mask(self.problem.nrWeeks,
                                                                         self.problem.nrDays,
                                                                         self.problem.slotsPerDay)

            overlaps = time_option_timeslots & unavailability_timeslots
            if np.count_nonzero(overlaps) > 0:
                return True

        return False

    def get_options_per_class(self):
        self.options_per_class = [1] * len(self.classes)
        self.classesWithoutRooms = np.empty(len(self.classes))
        for i, c in enumerate(self.classes):
            self.classesWithoutRooms[i] = len(c.room_options) == 0

            self.options_per_class[i] = max(len(c.room_options), 1) * len(c.time_options)

    def close_downwards_options(self, current_row, current_option):
        current_class = self.classes[current_row]

        current_class_row = self.decisionTable[current_row]

        current_class_options_unflattened = current_class_row[:self.options_per_class[current_row]].reshape(
            (-1, len(current_class.time_options)))

        if self.classesWithoutRooms[current_row] == 0:
            # class has a room, therefore we must check that no other lesson is scheduled in the same room at the same time
            room_option_idx, time_option_idx = np.unravel_index(np.array(current_option),
                                                                current_class_options_unflattened.shape)  # cast to array needed for cupy

            # # cast needed for cupy - numpy is unaffected
            # room_option_idx = int(room_option_idx)
            # time_option_idx = int(time_option_idx)

            selected_room = current_class.room_options[room_option_idx]
            selected_time = current_class.time_options[time_option_idx]

            selected_time_mask = selected_time.get_timeslots_mask(self.problem.nrWeeks, self.problem.nrDays,
                                                                  self.problem.slotsPerDay)

            for checking_class_index in range(current_row + 1, len(self.classes)):
                checking_class = self.classes[checking_class_index]
                checking_class_row = self.decisionTable[checking_class_index]
                checking_class_option_unflattened = checking_class_row[
                                                    :self.options_per_class[checking_class_index]].reshape(
                    (-1, len(checking_class.time_options)))

                room_mask = np.full(checking_class_option_unflattened.shape, False)
                if selected_room.id in checking_class.room_options_ids:
                    idx = checking_class.room_options_ids.index(selected_room.id)
                    room_mask[idx, :] = True

                    time_mask = np.full(checking_class_option_unflattened.shape, False)
                    for time_option_idx, time_option in enumerate(checking_class.time_options):
                        overlapping_time = np.count_nonzero(
                            selected_time_mask & time_option.get_timeslots_mask(self.problem.nrWeeks,
                                                                                self.problem.nrDays,
                                                                                self.problem.slotsPerDay)) > 0

                        if overlapping_time:
                            time_mask[:, time_option_idx] = True

                    closing_mask = (time_mask & room_mask).flat
                    closing_mask_padded = np.full(self.decisionTable.shape[1], False)

                    # numpy
                    closing_mask_padded[:len(closing_mask)] = closing_mask

                    # cupy
                    # closing_mask_padded[:len(closing_mask)] = closing_mask[:len(closing_mask)]

                    self.decisionTable[checking_class_index][closing_mask_padded] = -1  # close

    def solve(self):
        current_row = 0

        decision_table_stack = []
        class_list_stack = []

        current_option = 0

        while current_row < len(self.classes):
            # check if there is any row where all the options are closed - in which case we are ready to backtrack
            while np.any(np.all(self.decisionTable[current_row:], axis=1)):
                # backtrack
                self.decisionTable = decision_table_stack.pop()
                self.classes = class_list_stack.pop()
                print("backtrack from " + str(current_row) + " to " + str(current_row - 1))
                current_row -= 1
                option_to_close = np.where(self.decisionTable[current_row] == 1)

                self.decisionTable[current_row][option_to_close] = -1  # close previous row

            #  class with least open options
            next_class_offset = np.argmax(np.count_nonzero(self.decisionTable[current_row:], axis=1))
            self.classes[current_row], self.classes[next_class_offset + current_row] = self.classes[
                next_class_offset + current_row], self.classes[current_row]
            self.classesWithoutRooms[current_row], self.classesWithoutRooms[next_class_offset + current_row] = \
                self.classesWithoutRooms[next_class_offset + current_row], self.classesWithoutRooms[current_row]
            self.options_per_class[current_row], self.options_per_class[next_class_offset + current_row] = \
                self.options_per_class[next_class_offset + current_row], self.options_per_class[current_row]
            self.decisionTable[[current_row, next_class_offset + current_row]] = self.decisionTable[
                [next_class_offset + current_row, current_row]]

            open_options = np.where(self.decisionTable[current_row] == 0)[0]
            current_option = open_options[0]

            self.decisionTable[current_row, current_option] = 1
            decision_table_stack.append(np.copy(self.decisionTable))
            class_list_stack.append(self.classes.copy())

            self.close_downwards_options(current_row, current_option)

            print("proceeded from " + str(current_row) + " to " + str(current_row + 1))

            current_row += 1

    def get_result_as_gene(self):

        def decision_table_row_to_gene_decoder(i, row):
            idx = np.where(row == 1)[0]
            options_unflattened = row[:self.options_per_class[i]].reshape(
                (-1, len(self.classes[i].time_options)))
            room_idx, time_idx = np.unravel_index(idx, options_unflattened.shape);
            if self.classesWithoutRooms[i]:
                room_idx = [-1]
            return room_idx[0], time_idx[0]

        arr = [
            decision_table_row_to_gene_decoder(table_idx := self.classes.index(c), self.decisionTable[table_idx])
            for c in self.problem.classes
        ]

        return np.array(arr)
