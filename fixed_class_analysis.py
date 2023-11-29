# this class is not used in the final solution
# it is simply here to facilitate the ad hoc analysis of the input data


import glob
import os

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
    for dist in distributions_with_only_1_class:
        print(dist.type, dist.class_ids, dist.required, dist.penalty)

    distributions_with_no_penalty = []
    for d in problem.distributions:
        if d.penalty == 0 and not d.required:
            distributions_with_no_penalty.append(d)
    print("distributions with no penalty:", len(distributions_with_no_penalty))

    print("fixed:", len(fixed_classes))
    print("total:", len(problem.classes))
