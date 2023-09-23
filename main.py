import xml.etree.ElementTree as ET

from models.distribution import Distribution
from models.student import Student


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



    return problem


if __name__ == "__main__":
    file_path = "input.xml"
    problem = parse_xml(file_path)
