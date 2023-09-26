from models.input.config import Config


class Course:
    def __init__(self, id, configs: list[Config]):
        self.id = id
        self.configs = configs
