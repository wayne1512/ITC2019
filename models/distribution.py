class Distribution:
    def __init__(self, type, required, penalty, class_ids):
        self.class_ids = class_ids
        self.penalty = penalty
        self.required = required
        self.type = type
