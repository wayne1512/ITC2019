from typing import Final

from models.input.course import Course
from models.input.distribution import Distribution
from models.input.optimization import Optimization
from models.input.room import Room
from models.input.student import Student
from util import extract_class_list


class Problem:
    def __init__(self, name, nr_days, slots_per_day, nr_weeks, optimization: Optimization, rooms: list[Room],
                 courses: list[Course], distributions: list[Distribution], students: list[Student]):
        self.name: Final = name
        self.nrDays: Final = nr_days
        self.slotsPerDay: Final = slots_per_day
        self.nrWeeks: Final = nr_weeks
        self.optimization: Final = optimization
        self.rooms: Final = rooms
        self.courses: Final = courses
        self.distributions: Final = distributions
        self.students: Final = students

        self.__room_dict = {r.id: r for r in rooms}
        self.classes: Final = extract_class_list(self)
        self.__class_dict = {c.id: c for c in self.classes}

    def get_room_by_id(self, id):
        return self.__room_dict[id]

    def get_class_by_id(self, id):
        return self.__class_dict[id]

    def get_travel_time(self, room_id_1, room_id_2):
        travel = list(filter(lambda t: (t.room_id == room_id_2), self.get_room_by_id(room_id_1).travel))
        if len(travel) > 0:
            return travel[0].value

        travel = list(filter(lambda t: (t.room_id == room_id_1), self.get_room_by_id(room_id_2).travel))
        if len(travel) > 0:
            return travel[0].value

        return 0
