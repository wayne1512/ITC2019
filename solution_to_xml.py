import xml.etree.ElementTree as ET

from models.input.problem import Problem
from models.input.roomOption import RoomOption
from models.input.timeOption import TimeOption
from util import bool_arr_to_string


def generate_xml(problem: Problem, gene, file_path="output.xml"):
    problem_node = ET.Element('solution', name=problem.name, runtime='0', cores='0', technique='hybrid', author='test',
                              institution='test1', country='Malta')

    for c, r, t in zip(problem.classes, gene[:, 0], gene[:, 1]):
        to_chosen: TimeOption = c.time_options[t]
        el = ET.SubElement(problem_node, "class", id=str(c.id), start=str(to_chosen.start),
                           days=bool_arr_to_string(to_chosen.days),
                           weeks=bool_arr_to_string(to_chosen.weeks))

        if r>=0:
            ro_chosen = str(c.room_options[r].id)
            el.set("room",ro_chosen)


    tree = ET.ElementTree(problem_node)
    ET.indent(tree, "  ", 0)
    tree.write(open(file_path, 'wb'))
