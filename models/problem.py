from models.course import Course
from models.distribution import Distribution
from models.optimization import Optimization
from models.room import Room
from models.student import Student


class Problem:
    def __init__(self, name, nrDays, slotsPerDay, nrWeeks, optimization:Optimization, rooms:list[Room], courses:list[Course], distributions:list[Distribution], students:list[Student]):
        self.name = name
        self.nrDays = nrDays
        self.slotsPerDay = slotsPerDay
        self.nrWeeks = nrWeeks
        self.optimization = optimization
        self.rooms = rooms
        self.courses = courses
        self.distributions = distributions
        self.students = students
