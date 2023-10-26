import numpy as np


def calculate_clashes(problem, rooms_option_chosen_ids, time_option_chosen_ids):
    rooms_bookings = np.zeros((len(problem.rooms), problem.nrWeeks, problem.nrDays, problem.slotsPerDay))

    for idx, room in enumerate(problem.rooms):
        room_mask = room.get_unavailability_mask(problem.nrWeeks, problem.nrDays, problem.slotsPerDay)
        rooms_bookings[idx][room_mask] = -1

    room_clash_count = 0

    for i, c in enumerate(problem.classes):

        if rooms_option_chosen_ids[i] < 0:
            continue

        time_chosen = c.time_options[time_option_chosen_ids[i]]

        weeks = np.array(time_chosen.weeks)
        days = np.array(time_chosen.days)
        timeslots = np.full(problem.slotsPerDay, False)
        timeslots[time_chosen.start:time_chosen.start + time_chosen.length] = True

        mask = np.outer(np.outer(weeks, days), timeslots).reshape(
            (problem.nrWeeks, problem.nrDays, problem.slotsPerDay))

        room_option_chosen = c.room_options_ids[rooms_option_chosen_ids[i]]
        room_index = problem.rooms.index(problem.get_room_by_id(room_option_chosen))

        room_clash_count += np.count_nonzero(rooms_bookings[room_index][mask])

        update_mask = np.logical_and(mask, rooms_bookings[room_index] >= 0)

        rooms_bookings[room_index][update_mask] += 1

    return room_clash_count, 0


def clashes_close_downwards_option(solution_search, current_row, current_option):
    combined_closing_mask = np.full_like(solution_search.decisionTable, False, dtype=bool)

    current_class = solution_search.classes[current_row]

    current_class_row = solution_search.decisionTable[current_row]

    current_class_options_unflattened = current_class_row[:solution_search.options_per_class[current_row]].reshape(
        (-1, len(current_class.time_options)))

    if len(current_class.room_options) == 0:
        return combined_closing_mask

    room_option_idx, time_option_idx = np.unravel_index(current_option,
                                                        current_class_options_unflattened.shape)

    selected_room = current_class.room_options[room_option_idx]
    selected_time = current_class.time_options[time_option_idx]

    selected_time_mask = selected_time.get_timeslots_mask(solution_search.problem.nrWeeks,
                                                          solution_search.problem.nrDays,
                                                          solution_search.problem.slotsPerDay)

    for checking_class_index in range(current_row + 1, len(solution_search.classes)):
        checking_class = solution_search.classes[checking_class_index]
        checking_class_row = solution_search.decisionTable[checking_class_index]
        checking_class_option_unflattened = checking_class_row[
                                            :solution_search.options_per_class[checking_class_index]].reshape(
            (-1, len(checking_class.time_options)))

        room_mask = np.full(checking_class_option_unflattened.shape, False)
        if selected_room.id in checking_class.room_options_ids:
            idx = checking_class.room_options_ids.index(selected_room.id)
            room_mask[idx, :] = True

        time_mask = np.full(checking_class_option_unflattened.shape, False)
        for time_option_idx, time_option in enumerate(checking_class.time_options):
            overlapping_time = np.count_nonzero(
                selected_time_mask & time_option.get_timeslots_mask(solution_search.problem.nrWeeks,
                                                                    solution_search.problem.nrDays,
                                                                    solution_search.problem.slotsPerDay)) > 0

            if overlapping_time:
                time_mask[:, time_option_idx] = True

        closing_mask = (time_mask & room_mask).flat
        closing_mask_padded = np.full(solution_search.decisionTable.shape[1], False)
        closing_mask_padded[:len(closing_mask)] = closing_mask

        combined_closing_mask[checking_class_index][closing_mask_padded] = 1

    return combined_closing_mask
