import xml.etree.ElementTree as ET

import numpy as np

from models.clazz import Clazz
from models.config import Config
from models.course import Course
from models.distribution import Distribution
from models.optimization import Optimization
from models.problem import Problem
from models.room import Room
from models.roomOption import RoomOption
from models.student import Student
from models.subpart import Subpart
from models.timeOption import TimeOption
from models.travel import Travel
from models.unavailability import Unavailability


def bool_string_to_bool_arr(s):
    return [bool(int(c)) for c in s]


# Parse the XML file and create instances of the classes
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    students_elem = root.find("students")
    students = [Student(int(student.get("id")), [int(course.get("id")) for course in student.findall("course")]) for
                student in students_elem.findall("student")]

    distributions_elem = root.find("distributions")
    distributions = [Distribution(distribution.get("type"),
                                  bool(distribution.get("required") == 'true'),
                                  int(distribution.get("penalty") or 0),
                                  [int(clas.get("id")) for clas in distribution.findall("class")])
                     for distribution in distributions_elem.findall("distribution")]

    rooms_elem = root.find("rooms")
    rooms = [Room(
        int(room.get("id")),
        int(room.get("capacity")),
        [
            Travel(int(travel.get("room")), int(travel.get("value")))
            for travel in room.findall("travel")
        ],
        [
            Unavailability(
                bool_string_to_bool_arr(unavailability.get("days")),
                int(unavailability.get("start")),
                int(unavailability.get("length")),
                bool_string_to_bool_arr(unavailability.get("weeks"))
            )
            for unavailability in room.findall("unavailable")
        ]
    ) for room in rooms_elem.findall("room")]

    courses_elem = root.find("courses")
    courses = [
        Course(
            int(course.get("id")),
            [
                Config(
                    int(config.get("id")),
                    [
                        Subpart(
                            int(subpart.get("id")),
                            [
                                Clazz(
                                    int(clazz.get("id")),
                                    int(clazz.get("limit")),
                                    int(clazz.get("parent") or -1),
                                    [
                                        RoomOption(
                                            int(room.get("id")),
                                            int(room.get("penalty"))
                                        )
                                        for room in clazz.findall("room")
                                    ],
                                    [
                                        TimeOption(
                                            bool_string_to_bool_arr(time.get("days")),
                                            int(time.get("start")),
                                            int(time.get("length")),
                                            bool_string_to_bool_arr(time.get("weeks")),
                                            int(time.get("penalty")),
                                        )
                                        for time in clazz.findall("time")
                                    ]
                                )
                                for clazz in subpart.findall("class")
                            ]
                        )
                        for subpart in config.findall("subpart")
                    ]
                )
                for config in course.findall("config")
            ]
        )
        for course in courses_elem.findall("course")
    ]

    optimization_elem = root.find("optimization")
    optimization = Optimization(
        int(optimization_elem.get("time")),
        int(optimization_elem.get("room")),
        int(optimization_elem.get("distribution")),
        int(optimization_elem.get("student"))
    )

    problem = Problem(
        root.get("name"),
        int(root.get("nrDays")),
        int(root.get("slotsPerDay")),
        int(root.get("nrWeeks")),
        optimization,
        rooms,
        courses,
        distributions,
        students
    )

    return problem

def random_gene(problem:Problem,maximums):
    return (np.random.rand(*maximums.shape)*maximums).astype(int)

def get_gene_maximums(problem:Problem):
    classes:list[Clazz] = []

    for course in problem.courses:
        for conf in course.configs:
            for sp in conf.subparts:
                classes += sp.classes

    geneMaximums = [
        (len(c.room_options),len(c.time_options))
        for c in classes
    ]

    return np.array(geneMaximums)

if __name__ == "__main__":
    file_path = "input.xml"
    problem = parse_xml(file_path)

    maximumGenes = get_gene_maximums(problem)
    print(maximumGenes)
    rand = random_gene(problem, maximumGenes)
    print(rand)
