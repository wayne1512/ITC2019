from models.subpart import Subpart


class Config:
    def __init__(self, id, subparts:list[Subpart]):
        self.id = id
        self.subparts = subparts
