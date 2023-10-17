import numpy as np


def calculate_clashes(problem, classes, rooms_option_chosen_ids, time_option_chosen_ids):
    rooms_bookings = np.zeros((len(problem.rooms), problem.nrWeeks, problem.nrDays, problem.slotsPerDay))

    for idx, room in enumerate(problem.rooms):
        room_mask = room.get_unavailability_mask(problem.nrWeeks, problem.nrDays, problem.slotsPerDay)
        rooms_bookings[idx][room_mask] = -1

    room_clash_count = 0

    for i, c in enumerate(classes):

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
