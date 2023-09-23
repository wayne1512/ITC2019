class Room:
    def __init__(self, id, capacity, unavailabilities = None):
        self.unavailabilities = unavailabilities or []
        self.capacity = capacity
        self.id = id

