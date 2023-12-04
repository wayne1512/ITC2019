from models.input.roomOption import RoomOption
from models.input.timeOption import TimeOption


class Clazz:
    def __init__(self, id, limit, parent_id, room_options: list[RoomOption], time_options: list[TimeOption]):
        self.id = id
        self.limit = limit
        self.parent_id = parent_id
        self.room_options = room_options
        self.time_options = time_options

        self.room_options_ids = [opt.id for opt in room_options]

        self.closed_room_time_combinations = None

        # pre-placed means that the class has been placed in a fixed room and time
        # and the time has been added as an unavailable time for the room
        # the double booking penalty for this class will be skipped
        self.pre_placed = False

    def is_fixed(self):
        return len(self.room_options) <= 1 and len(self.time_options) == 1
