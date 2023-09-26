from xml.etree import ElementTree as ET

from models.input.clazz import Clazz
from models.input.config import Config
from models.input.course import Course
from models.input.distribution import Distribution
from models.input.optimization import Optimization
from models.input.problem import Problem
from models.input.room import Room
from models.input.roomOption import RoomOption
from models.input.student import Student
from models.input.subpart import Subpart
from models.input.timeOption import TimeOption
from models.input.travel import Travel
from models.input.unavailability import Unavailability
from util import bool_string_to_bool_arr


# Parse the XML file into objects
def parse_xml(file_path) -> Problem:
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
