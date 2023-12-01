# this class is not used in the final solution
# it is simply here to facilitate the ad hoc analysis of the input data


import glob
import os

import networkx as nx
import numpy as np

from parse_input import parse_xml


def find_xml_files(root_folder):
    xml_files = []

    # Walk through the directory tree
    for foldername, subfolders, filenames in os.walk(root_folder):
        # Use glob to find XML files in the current folder
        xml_files.extend(glob.glob(os.path.join(foldername, '*.xml')))

    return xml_files


# Replace 'your_folder_path' with the path to your folder containing subfolders with XML files
folder_path = 'D:\\Downloads\\assignmentRedownload\\instances'
xml_files = find_xml_files(folder_path)


def analyze_subinstances():
    global d, c, i
    graph = nx.Graph()
    for d in problem.distributions:
        for c in d.class_ids:
            for c2 in d.class_ids:
                if c != c2:
                    course1 = problem.get_course_by_class_id(c)
                    course2 = problem.get_course_by_class_id(c2)
                    # distribution d affects these 2 courses, these classes are therefore in the same sub-instance
                    if course1 != course2:
                        graph.add_edge(course1.id, course2.id)
    for i, c1 in enumerate(problem.classes):
        for c2 in problem.classes[i + 1:]:
            common_rooms = [r.id for r in c1.room_options if r.id in {r2.id for r2 in c2.room_options}]
            if common_rooms:
                course1 = problem.get_course_by_class_id(c1.id)
                course2 = problem.get_course_by_class_id(c2.id)
                if course1 != course2:
                    graph.add_edge(course1.id, course2.id)
    for s in problem.students:
        for course in s.course_ids:
            for course2 in s.course_ids:
                if course != course2:
                    graph.add_edge(course, course2)
    # nx.draw(graph, with_labels=True)
    # plt.show()
    islands = list(nx.connected_components(graph))
    print("islands:", [len(i) for i in islands])
    print("nr of islands:", len(islands))


# Print the list of XML files
for xml_file in xml_files:
    print(xml_file)
    problem = parse_xml(xml_file)

    fixed_classes = []
    for c in problem.classes:
        if len(c.room_options) <= 1 and len(c.time_options) == 1:
            fixed_classes.append(c)

    distributions_per_fixed_class = []

    for i, c in enumerate(fixed_classes):
        distributions_for_class = []
        for d in problem.distributions:
            if c.id in d.class_ids:
                distributions_for_class.append(d)
        distributions_per_fixed_class.append(distributions_for_class)

    distributions_with_only_1_class = []
    for d in problem.distributions:
        if len(d.class_ids) == 1:
            distributions_with_only_1_class.append(d)

    print("distributions with only 1 class:", len(distributions_with_only_1_class))
    # for dist in distributions_with_only_1_class:
    #     print(dist.type, dist.class_ids, dist.required, dist.penalty)

    distributions_with_no_penalty = []
    for d in problem.distributions:
        if d.penalty == 0 and not d.required:
            distributions_with_no_penalty.append(d)
    print("distributions with no penalty:", len(distributions_with_no_penalty))

    analyze_subinstances()

    room_time_combinations_closed = []

    for c in problem.classes:

        if len(c.room_options) == 0:
            continue

        for ro in c.room_options:
            room = problem.get_room_by_id(ro.id)
            room_unavailabilities = room.unavailabilities
            for to in c.time_options:
                for ru in room_unavailabilities:
                    if not (
                            to.start >= (ru.start + ru.length) or
                            ru.start >= (to.start + to.length) or
                            not np.any(np.logical_and(to.days, ru.days)) or
                            not np.any(np.logical_and(to.weeks, ru.weeks))
                    ):
                        room_time_combinations_closed.append((c, ro, to))
                        break

    print("room time combinations closed:", len(room_time_combinations_closed))

    print("fixed:", len(fixed_classes))
    print("total:", len(problem.classes))
