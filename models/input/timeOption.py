import numpy as np


class TimeOption:
    def __init__(self, days, start, length, weeks, penalty):
        self.days = days
        self.start = start
        self.length = length
        self.weeks = weeks
        self.penalty = penalty

    def get_timetable_mask(self, nrWeeks, nrDays, slotsPerDay):
        weeks = np.array(self.weeks)
        days = np.array(self.days)
        timeslots = np.full(slotsPerDay, False)
        timeslots[self.start:self.start + self.length] = True

        mask = np.outer(np.outer(weeks, days), timeslots).reshape(
            (nrWeeks, nrDays, slotsPerDay))

        return mask
