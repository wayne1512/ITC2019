import numpy as np

from models.input.problem import Problem


class SolutionSearch:
    def __init__(self, problem: Problem):
        self.options_per_class = None
        self.classes_without_rooms = None
        self.decision_table = None

        self.classes = problem.classes.copy()
        self.problem = problem

        self.setup_decision_table()

    def setup_decision_table(self):
        self.get_options_per_class()

        self.decision_table = np.full((len(self.classes), max(self.options_per_class)), -1)

        for i, c in enumerate(self.options_per_class):
            self.decision_table[i, :c] = 0
            checking_class = self.classes[i]

            # close unavailable rooms
            unflattened_class_choices = self.decision_table[i][
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
        self.classes_without_rooms = np.empty(len(self.classes))
        for i, c in enumerate(self.classes):
            self.classes_without_rooms[i] = len(c.room_options) == 0

            self.options_per_class[i] = max(len(c.room_options), 1) * len(c.time_options)

    def swap_rows(self, i1, i2):
        self.classes[i1], self.classes[i2] = self.classes[
            i2], self.classes[i1]
        self.classes_without_rooms[i1], self.classes_without_rooms[i2] = \
            self.classes_without_rooms[i2], self.classes_without_rooms[i1]
        self.options_per_class[i1], self.options_per_class[i2] = \
            self.options_per_class[i2], self.options_per_class[i1]
        self.decision_table[[i1, i2]] = self.decision_table[
            [i2, i1]]

    def get_result_as_gene(self):

        def decision_table_row_to_gene_decoder(i, row):
            idx = np.where(row == 1)[0]
            options_unflattened = row[:self.options_per_class[i]].reshape(
                (-1, len(self.classes[i].time_options)))
            room_idx, time_idx = np.unravel_index(idx, options_unflattened.shape)
            if self.classes_without_rooms[i]:
                room_idx = [-1]
            return room_idx[0], time_idx[0]

        arr = [
            decision_table_row_to_gene_decoder(table_idx := self.classes.index(c), self.decision_table[table_idx])
            for c in self.problem.classes
        ]

        return np.array(arr)
