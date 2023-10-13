import util


class Unavailability:
    def __init__(self, days, start, length, weeks):
        self.days = days
        self.start = start
        self.length = length
        self.weeks = weeks
        self.timetable_mask_memo = None

    def get_timeslots_mask(self, nr_weeks, nr_days, slots_per_day):
        if self.timetable_mask_memo is None:
            self.timetable_mask_memo = util.generate_timeslots_mask(self.weeks, self.days, self.start, self.length,
                                                                    nr_weeks, nr_days, slots_per_day)

        return self.timetable_mask_memo
