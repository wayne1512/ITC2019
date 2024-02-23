from collections import Counter
from xml.etree import ElementTree as ET

import numpy as np

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


def parse_itc2007_post_enrolment(file_path) -> Problem:
    input_file = open(file_path, "r")

    daysInTable = 5
    timeslotsPerDay = 9

    event_count, room_count, feature_count, student_count = [int(x) for x in next(input_file).split()]

    room_sizes = np.array([int(next(input_file)) for _ in range(room_count)])

    student_event_matrix = np.array([bool(int(next(input_file))) for _ in range(student_count * event_count)]).reshape(
        (student_count, event_count))

    room_feature_matrix = np.array([bool(int(next(input_file))) for _ in range(room_count * feature_count)]).reshape(
        (room_count, feature_count))

    event_feature_matrix = np.array([bool(int(next(input_file))) for _ in range(event_count * feature_count)]).reshape(
        (event_count, feature_count))

    availability_matrix = np.array([bool(int(next(input_file))) for _ in range(event_count * daysInTable *
                                                                               timeslotsPerDay)]).reshape(
        (event_count, daysInTable * timeslotsPerDay))

    before_matrix = np.array([int(next(input_file)) for _ in range(event_count * event_count)]).reshape(
        (event_count, event_count))

    events_student_count = np.sum(student_event_matrix, axis=0)

    event_room_matrix = np.zeros((event_count, room_count), dtype=bool)

    for event_id in range(event_count):
        for room_id in range(room_count):
            # this part handles HC2
            # In each case the room should be big enough for all the attending students and should satisfy
            # all of the features required by the event;
            if events_student_count[event_id] <= room_sizes[room_id]:  # room is big enough
                event_room_matrix[event_id, room_id] = (
                    np.where(event_feature_matrix[event_id], room_feature_matrix[room_id],
                             True).all())  # room has all the features

    # transform
    rooms = [Room(i, size, [], []) for i, size in enumerate(room_sizes)]
    courses = [
        Course(
            i,
            [
                Config(
                    i,
                    [
                        Subpart(
                            i,
                            [
                                Clazz(i,
                                      student_count,
                                      -1,
                                      [
                                          RoomOption(room_id, 0)
                                          for room_id in np.argwhere(event_room_matrix[i] == 1)[:, 0]
                                      ],
                                      [
                                          # this part handles HC4
                                          # Events should only be assigned to timeslots that are pre-defined as
                                          # “available” for those events
                                          TimeOption(
                                              np.arange(daysInTable) == day,
                                              start,
                                              1,
                                              [True],
                                              # SC1 Students should not be scheduled to attend an event in the last
                                              # timeslot of a day (that is, timeslots 9, 18, 27, 36, or 45);
                                              #
                                              # in this case - since we already unraveled the array into day, start
                                              # the last timeslot of a day is timeslotsPerDay - 1
                                              0 if (start != (timeslotsPerDay - 1)) else events_student_count[i]
                                          )
                                          for (day, start) in np.column_stack
                                          ((
                                          np.unravel_index(np.argwhere(availability_matrix[i])[:, 0],
                                                           (daysInTable, timeslotsPerDay))
                                      ))
                                      ]
                                      )
                            ]
                        )
                    ]
                )
            ]
        )
        for i in range(event_count)
    ]

    optimization = Optimization(1, 1, 1, 1)

    students = [Student(i, np.argwhere(student_event_matrix[i])[:, 0]) for i in range(student_count)]

    # HC1 - No student should be required to attend more than one event at the same time;
    hc1_distributions = [Distribution("NonOverlap", True, None, s.course_ids) for s in students]

    # HC5 - Where specified, events should be scheduled to occur in the correct order in the week.
    hc5_distributions = [Distribution("Precedence", True, None, [i, j]) for i, j in np.argwhere(before_matrix == 1)]

    # this allows us to group together students that are taking the same exact courses
    # and only do 1 distribution for all of them
    students_course_tuple_list = [tuple(s.course_ids) for s in students]
    students_course_list_counter = Counter(students_course_tuple_list)

    # SC2 - Students should not have to attend three (or more) events in successive timeslots occurring in the same day;
    sc2_distributions = [Distribution("ITC2007MaxConsecutive(2)", False, count, list(lst))
                         for lst, count in students_course_list_counter.items()]

    # SC3 - Students should not be required to attend only one event in a particular day.
    sc3_distributions = [Distribution("ITC2007MinDayLoad(2)", False, count, list(lst))
                         for lst, count in students_course_list_counter.items()]

    distributions = hc1_distributions + hc5_distributions + sc2_distributions + sc3_distributions

    problem = Problem(
        "ITC2007",
        daysInTable,
        timeslotsPerDay,
        1,
        optimization,
        rooms,
        courses,
        distributions,
        students
    )
    return problem
