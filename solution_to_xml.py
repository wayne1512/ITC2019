import xml.etree.ElementTree as ET

import numpy as np

from models.input.problem import Problem
from models.input.timeOption import TimeOption
from util import bool_arr_to_string


def generate_xml(problem: Problem, gene, student_classes: dict, file_path="output.xml"):
    class_students = {}

    for s_id, c_ids in student_classes.items():
        for c_id in c_ids:
            if c_id not in class_students:
                class_students[c_id] = []
            class_students[c_id].append(s_id)

    problem_node = ET.Element('solution', name=problem.name, runtime='0', cores='0', technique='hybrid',
                              author='Wayne Borg', institution='University of Malta: Faculty of ICT', country='Malta')

    for c, r, t in zip(problem.classes, gene[:, 0], gene[:, 1]):
        to_chosen: TimeOption = c.time_options[t]
        el = ET.SubElement(problem_node, "class", id=str(c.id), start=str(to_chosen.start),
                           days=bool_arr_to_string(to_chosen.days),
                           weeks=bool_arr_to_string(to_chosen.weeks))

        if r>=0:
            ro_chosen = str(c.room_options[r].id)
            el.set("room",ro_chosen)

        for s_id in class_students.get(c.id, []):
            ET.SubElement(el, "student", id=str(s_id))

    tree = ET.ElementTree(problem_node)
    ET.indent(tree, "  ", 0)
    tree.write(open(file_path, 'wb'))


def output_itc2007_cb(problem: Problem, gene, raw_room_ids, raw_course_ids_for_classes, file_path="output.sol"):
    f = open(file_path, "w+")

    for c, r, t, in zip(problem.classes, gene[:, 0], gene[:, 1]):
        to_chosen: TimeOption = c.time_options[t]

        ro_chosen = c.room_options[r]
        room_name = raw_room_ids[ro_chosen.id]

        course_name = raw_course_ids_for_classes[c.id]

        day_name = np.where(to_chosen.days)[0][0]
        slot_name = to_chosen.start

        f.write(f"{course_name} {room_name} {day_name} {slot_name}\n")
