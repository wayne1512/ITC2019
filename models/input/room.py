import numpy as np

from models.input.travel import Travel
from models.input.unavailability import Unavailability


class Room:
    def __init__(self, id, capacity, travel: list[Travel], unavailabilities: list[Unavailability] = None):
        self.id = id
        self.capacity = capacity
        self.travel = travel
        self.unavailabilities: list[Unavailability] = unavailabilities or []

        self.unavailability_mask_params = None
        self.room_mask = None

    def get_unavailability_mask(self, nrWeeks, nrDays, slotsPerDay):

        if self.room_mask is not None and self.unavailability_mask_params == (nrWeeks, nrDays, slotsPerDay):
            return self.room_mask  # memoization

        unavailability_mask_params = (nrWeeks, nrDays, slotsPerDay)
        room_mask = np.full((nrWeeks, nrDays, slotsPerDay), False)

        for u in self.unavailabilities:
            timeslots = np.full(slotsPerDay, False)
            timeslots[u.start:u.start + u.length] = True

            mask = np.outer(np.outer(np.array(u.weeks), np.array(u.days)), timeslots).reshape(
                (nrWeeks, nrDays, slotsPerDay))
            room_mask = room_mask | mask

        self.room_mask = room_mask
        self.unavailability_mask_params = unavailability_mask_params

        return room_mask
