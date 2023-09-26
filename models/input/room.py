class Room:
    def __init__(self, id, capacity, travel, unavailabilities=None):
        self.id = id
        self.capacity = capacity
        self.travel = travel
        self.unavailabilities = unavailabilities or []
