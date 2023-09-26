from models.clazz import Clazz


class Subpart:
    def __init__(self, id, classes:list[Clazz]):
        self.id = id
        self.classes = classes
