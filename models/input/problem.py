from models.input.course import Course
from models.input.distribution import Distribution
from models.input.optimization import Optimization
from models.input.room import Room
from models.input.student import Student


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
