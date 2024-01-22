import random

from object import Object


class SidewalkObject(Object):
    def __init__(self, group, x, y, range_y, player_speed):
        super().__init__(group, x, y, f"sidewalk_object{random.randrange(1, 17)}.png", [x, x],
                         range_y, player_speed)


