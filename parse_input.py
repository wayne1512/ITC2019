from collections import Counter
from typing import Tuple
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
def parse_xml(file_path) -> Tuple[Problem, dict]:
    statistics = {}

    tree = ET.parse(file_path)
    root = tree.getroot()

    statistics["name"] = root.get("name")

    students_elem = root.find("students")
    students = [Student(int(student.get("id")), [int(course.get("id")) for course in student.findall("course")]) for
                student in students_elem.findall("student")]
    statistics["student_count"] = len(students)

    if len(students) > 0:
        statistics["avg_courses_per_student"] = np.mean([len(student.course_ids) for student in students])
    else:
        statistics["avg_courses_per_student"] = np.nan

    distributions_elem = root.find("distributions")
    distributions = [Distribution(distribution.get("type"),
                                  bool(distribution.get("required") == 'true'),
                                  int(distribution.get("penalty") or 0),
                                  [int(clas.get("id")) for clas in distribution.findall("class")])
                     for distribution in distributions_elem.findall("distribution")]
    statistics["distribution_count"] = len(distributions)
    statistics["avg_classes_per_distribution"] = np.mean([len(distribution.class_ids)
                                                          for distribution in distributions])
    statistics["avg_penalty_per_soft_distribution"] = np.mean([distribution.penalty for distribution in distributions
                                                               if not distribution.required])
    statistics["hard_distribution_count"] = len([distribution for distribution in distributions
                                                 if distribution.required])
    statistics["soft_distribution_count"] = len([distribution for distribution in distributions
                                                 if not distribution.required])

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

    statistics["room_count"] = len(rooms)

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

    statistics["course_count"] = len(courses)
    statistics["class_count"] = sum(
        [len(subpart.classes) for course in courses for config in course.configs for subpart in config.subparts])

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

    statistics["nrDays"] = int(root.get("nrDays"))
    statistics["slotsPerDay"] = int(root.get("slotsPerDay"))
    statistics["nrWeeks"] = int(root.get("nrWeeks"))

    return problem, statistics


def parse_itc2007_curriculum_based(file_path) -> Tuple[Problem, dict]:
    statistics = {}

    input_file = open(file_path, "r")

    name = next(input_file).strip().split()[1]
    course_count = int(next(input_file).strip().split()[1])
    room_count = int(next(input_file).strip().split()[1])
    days = int(next(input_file).strip().split()[1])
    periods_per_day = int(next(input_file).strip().split()[1])
    curricula_count = int(next(input_file).strip().split()[1])
    constraint_count = int(next(input_file).strip().split()[1])

    statistics["name"] = name
    statistics["course_count"] = course_count
    statistics["room_count"] = room_count
    statistics["days"] = days
    statistics["periods_per_day"] = periods_per_day
    statistics["curricula_count"] = curricula_count
    statistics["constraint_count"] = constraint_count

    while next(input_file).strip() != "COURSES:":
        pass

    raw_courses = [next(input_file).strip().split() for _ in range(course_count)]

    while next(input_file).strip() != "ROOMS:":
        pass

    raw_rooms = [next(input_file).strip().split() for _ in range(room_count)]

    while next(input_file).strip() != "CURRICULA:":
        pass

    raw_curricula = [next(input_file).strip().split() for _ in range(curricula_count)]

    while next(input_file).strip() != "UNAVAILABILITY_CONSTRAINTS:":
        pass

    raw_constraints = [next(input_file).strip().split() for _ in range(constraint_count)]

    raw_room_id_to_room_id = {}
    rooms = []

    for i, raw_room in enumerate(raw_rooms):
        raw_room_id = raw_room[0]
        capacity = int(raw_room[1])
        travel_times = []
        unavailabilities = []
        raw_room_id_to_room_id[raw_room_id] = i
        rooms.append(Room(i, capacity, travel_times, unavailabilities))

    unavailabilities_per_course = {}
    for raw_constraint in raw_constraints:
        course_id = raw_constraint[0]
        day = int(raw_constraint[1])
        period = int(raw_constraint[2])

        if course_id not in unavailabilities_per_course:
            unavailabilities_per_course[course_id] = []

        unavailabilities_per_course[course_id].append((day, period))

    statistics["average_unavailabilities_per_course"] = (
            np.sum([len(unavailabilities) for unavailabilities in unavailabilities_per_course.values()])
            / course_count)

    raw_course_id_to_class_ids = {}
    teachers_to_class_ids = {}
    next_class_id = 0

    courses = []

    sc2_distributions = []
    sc4_distributions = []

    statistics["lecture_count"] = (np.sum([int(raw_course[2]) for raw_course in raw_courses]))
    statistics["average_lectures_per_course"] = statistics["lecture_count"] / course_count

    for i, raw_course in enumerate(raw_courses):
        course_id = raw_course[0]
        teacher = raw_course[1]
        nr_of_lectures = int(raw_course[2])
        min_working_days = int(raw_course[3])
        nr_of_students = int(raw_course[4])

        class_ids = []
        classes = []

        for j in range(nr_of_lectures):
            clazz_id = next_class_id
            next_class_id += 1
            class_ids.append(clazz_id)

            room_options = []
            for room_id in range(room_count):
                # SC1 - , the number of students that attend the course must be less or equal than the number
                # of seats of all the rooms that host its lectures
                room_options.append(RoomOption(room_id, max(0, nr_of_students - rooms[room_id].capacity)))

            time_options = []
            for day in range(days):
                for period in range(periods_per_day):
                    if not (day, period) in unavailabilities_per_course.get(course_id, []):
                        time_options.append(TimeOption(np.arange(days) == day, period, 1, [True], 0))

            classes.append(Clazz(clazz_id, nr_of_students, None, room_options, time_options))

        courses.append(
            Course(course_id, [Config(i, [Subpart(i, classes)])]))

        raw_course_id_to_class_ids[course_id] = class_ids

        # SC2 - The lectures of each course must be spread into the given minimum number of days.
        # Each day below the minimum counts as 5 points of penalty.
        sc2_distributions.append(Distribution(f"ITC2007MinDays({str(min_working_days)})", False, 5, class_ids))

        # SC4 - All lectures of a course should be given in the same room.
        # Each distinct room used for the lectures of a course, but the first, counts as 1 point of penalty.
        sc4_distributions.append(Distribution("ITC2007SameRoom", False, 1, class_ids))

        if teacher not in teachers_to_class_ids:
            teachers_to_class_ids[teacher] = class_ids.copy()
        teachers_to_class_ids[teacher] = teachers_to_class_ids[raw_course[1]] + class_ids.copy()

    statistics["teacher_count"] = len(teachers_to_class_ids)
    statistics["average_lectures_per_teacher"] = statistics["lecture_count"] / len(teachers_to_class_ids)

    # HC3 - Lectures of courses in the same curriculum or taught by the same teacher must be all
    # scheduled in different periods

    # SC3 - Lectures belonging to a curriculum should be adjacent to each other (i.e., in consecutive periods).
    # For a given curriculum, we account for a violation every time there is one lecture not adjacent
    # to any other lecture within the same day. Each isolated lecture in a curriculum counts as 2 points of penalty.

    hc3_distributions_teachers = [Distribution("NonOverlap", True, None, class_ids)
                                  for teacher, class_ids in teachers_to_class_ids.items() if len(class_ids) > 1]
    hc3_distributions_curriculum = []

    sc3_distributions = []

    for raw_curriculum in raw_curricula:
        curriculum_id = raw_curriculum[0]
        class_ids = []
        for course_id in raw_curriculum[2:]:
            class_ids += raw_course_id_to_class_ids[course_id]
        hc3_distributions_curriculum.append(Distribution("NonOverlap", True, None, class_ids))
        hc3_distributions_curriculum.append(Distribution("ITC2007NotIsolated", False, 2, class_ids))

    distributions = (hc3_distributions_teachers + hc3_distributions_curriculum +
                     sc2_distributions + sc3_distributions + sc4_distributions)

    problem = Problem(
        name,
        days,
        periods_per_day,
        1,
        Optimization(1, 1, 1, 1),
        rooms,
        courses,
        distributions,
        []
    )

    return problem, statistics


def parse_itc2007_post_enrolment(file_path) -> Tuple[Problem, dict]:
    input_file = open(file_path, "r")

    statistics = {}

    daysInTable = 5
    timeslotsPerDay = 9

    statistics["daysInTable"] = daysInTable
    statistics["timeslotsPerDay"] = timeslotsPerDay

    event_count, room_count, feature_count, student_count = [int(x) for x in next(input_file).split()]

    statistics["event_count"] = event_count
    statistics["room_count"] = room_count
    statistics["feature_count"] = feature_count
    statistics["student_count"] = student_count

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
    return problem, statistics
