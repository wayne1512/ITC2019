import numpy as np
import pandas as pd


class UnavailableRoomHelper:

    def __init__(self, problem):
        self.problem = problem

    def count_violations(self, time_options_chosen, rooms_options_chosen):

        violation_count = 0

        for i in range(len(time_options_chosen)):

            clazz = self.problem.classes[i]
            if clazz.pre_placed:
                continue

            room_option = rooms_options_chosen[i]
            time_option = time_options_chosen[i]

            if room_option is not None:
                room = self.problem.get_room_by_id(room_option.id)
                room_unavailabilities = room.unavailabilities

                for ru in room_unavailabilities:
                    if not (
                            time_option.start >= (ru.start + ru.length) or
                            ru.start >= (time_option.start + time_option.length) or
                            not np.any(np.logical_and(time_option.days, ru.days)) or
                            not np.any(np.logical_and(time_option.weeks, ru.weeks))
                    ):
                        violation_count += 1
                        break

        return violation_count

    def count_violations_editable(self, time_options_chosen, rooms_options_chosen):

        violations = []

        for i in range(len(time_options_chosen)):

            clazz = self.problem.classes[i]
            if clazz.pre_placed:
                continue

            room_option = rooms_options_chosen[i]
            time_option = time_options_chosen[i]

            if room_option is not None:
                room = self.problem.get_room_by_id(room_option.id)
                room_unavailabilities = room.unavailabilities

                for ru in room_unavailabilities:
                    if not (
                            time_option.start >= (ru.start + ru.length) or
                            ru.start >= (time_option.start + time_option.length) or
                            not np.any(np.logical_and(time_option.days, ru.days)) or
                            not np.any(np.logical_and(time_option.weeks, ru.weeks))
                    ):
                        violations.append({'class': i})

        return pd.DataFrame(violations, columns=['class'])

    def count_violations_relating_to_classes(self, rooms_options_chosen, time_options_chosen, indexes):
        violations = []

        for i in indexes:
            for i in range(len(time_options_chosen)):

                clazz = self.problem.classes[i]
                if clazz.pre_placed:
                    continue

                room_option = rooms_options_chosen[i]
                time_option = time_options_chosen[i]

                if room_option is not None:
                    room = self.problem.get_room_by_id(room_option.id)
                    room_unavailabilities = room.unavailabilities

                    for ru in room_unavailabilities:
                        if not (
                                time_option.start >= (ru.start + ru.length) or
                                ru.start >= (time_option.start + time_option.length) or
                                not np.any(np.logical_and(time_option.days, ru.days)) or
                                not np.any(np.logical_and(time_option.weeks, ru.weeks))
                        ):
                            violations.append({'class': i})

        return pd.DataFrame(violations)

    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = self.problem.classes
        classes_index = range(len(classes))

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]
        rooms_options_chosen = [c.room_options[rooms_option_chosen_ids[idx]] if len(c.room_options) > 0 else None for
                                c, idx in zip(classes, classes_index)]

        violation_count = self.count_violations(time_options_chosen, rooms_options_chosen)

        return violation_count, 0

    def calculate_clashes_editable(self, rooms_option_chosen_ids, time_option_chosen_ids):
        classes = self.problem.classes
        classes_index = range(len(classes))

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]
        rooms_options_chosen = [c.room_options[rooms_option_chosen_ids[idx]] if len(c.room_options) > 0 else None for
                                c, idx in zip(classes, classes_index)]

        violations = self.count_violations_editable(time_options_chosen, rooms_options_chosen)

        return violations

    def edit_calculation(self, rooms_option_chosen_ids, time_option_chosen_ids, violations, changed_indexes,
                         changed_class_ids):

        classes = self.problem.classes
        classes_index = range(len(classes))

        time_options_chosen = [c.time_options[time_option_chosen_ids[idx]] for c, idx in zip(classes, classes_index)]
        rooms_options_chosen = [c.room_options[rooms_option_chosen_ids[idx]] if len(c.room_options) > 0 else None for
                                c, idx in zip(classes, classes_index)]

        filtered_df = violations[~violations['class'].isin(changed_indexes)].copy()

        new_violations = self.count_violations_relating_to_classes(rooms_options_chosen, time_options_chosen,
                                                                   changed_indexes)

        return pd.concat([filtered_df, new_violations])
