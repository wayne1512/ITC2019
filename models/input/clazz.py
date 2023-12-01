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
