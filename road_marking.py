from object import Object
import pygame


class RoadMarking(Object):
    def __init__(self, group, width, height, x, y, y_range, player_speed):
        self.image = pygame.Surface([width, height])
        self.image.fill(pygame.Color("white"))
        super().__init__(group, x, y, None, [x, x], y_range, player_speed)


