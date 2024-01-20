import pygame
from cars import UserCar


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.game_is_over = False

    def update_player_speed_data(self, new_player_speed):
        for sprite in self.sprites():
            if not isinstance(sprite, UserCar):
                sprite.update_player_speed_data(new_player_speed)

    def game_over(self):
        self.game_is_over = True
        for sprite in self.sprites():
            sprite.stop()


