import random
from collections import deque
from typing import List


class RandomStudentSectioning:
    def __init__(self, problem, seed=42):
        self.problem = problem
        self.seed = seed
        self.rng = random.Random(seed)
        random.seed(seed)

    def apply(self):
        students: List = self.problem.students

        res = {}
        class_enrolment_count = {c.id: 0 for c in self.problem.classes}

        for s in students:

            student_chosen_class_ids = []

            courses = s.course_ids
            for c_id in courses:
                # get course with id
                course = next(c for c in self.problem.courses if c.id == c_id)

                config_placements_success = False

                while not config_placements_success:
                    # choose a random config
                    config = self.rng.choice(course.configs)

                    config_placements = self.choose_classes_in_config(class_enrolment_count, config.subparts)

                    if config_placements is None:
                        continue
                    else:
                        config_placements_success = True
                        student_chosen_class_ids.extend(config_placements)

            res[s.id] = student_chosen_class_ids
        return res

    def choose_classes_in_config(self, class_enrolment_count, subparts):

        subparts_queue = deque(subparts)

        failed_placements = 0
        chosen_class_ids = []
        while len(subparts_queue) > 0 and failed_placements < len(subparts):
            subpart = subparts_queue.popleft()
            classes = subpart.classes

            classes = [c for c in classes if (c.parent_id is None or c.parent_id == -1
                                              or c.parent_id in chosen_class_ids)
                       and class_enrolment_count[c.id] < c.limit]

            if len(classes) > 0:
                # choose a random class
                clazz = self.rng.choice(classes)
                chosen_class_ids.append(clazz.id)
                class_enrolment_count[clazz.id] += 1
                failed_placements = 0
            else:
                subparts_queue.append(subpart)
                failed_placements += 1

        if len(subparts_queue) == 0:
            return chosen_class_ids

        return None
