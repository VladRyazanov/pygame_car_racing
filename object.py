import pygame

from load_image import load_image


class Object(pygame.sprite.Sprite):
    """
    Класс всех объектов на экране. От него наследуются такие классы, как Car, RoadMarking и т.д
    """
    def __init__(self, group, x, y, image_file_name, x_range, y_range, player_speed, is_moving_back=False):
        super().__init__(group)
        self.is_moving_back = is_moving_back
        if image_file_name is not None:
            self.image = load_image(image_file_name, flip_image=self.is_moving_back)

        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # x_range и y_range - это диапазоны координат, в которых может находиться объект. Например,
        # машины не могут заезжать за края дороги
        self.x_range = x_range[0], x_range[1] - self.image.get_width()
        self.y_range = y_range[0] - self.image.get_height() * 2, y_range[1] + self.image.get_height()

        # свйство player_speed сделано для того, чтобы перемещать данный объект относительно экрана,
        # создавая эффект движения пользователя
        self.player_speed = player_speed
        self.speed = 0
        self.acceleration = 0
        self.turning_speed = 0

    def move(self, x=None, y=None, change_x_by=0, change_y_by=0):
        new_x = x if x is not None else self.rect.x
        new_y = y if y is not None else self.rect.y
        self.rect = self.image.get_rect().move(min(max(self.x_range[0], new_x + change_x_by), self.x_range[1]),
                                               new_y + change_y_by)

    def set_speed(self, new_speed):
        self.speed = new_speed if not self.is_moving_back else -new_speed

    def set_turning_speed(self, new_turning_speed):
        if self.speed != 0:
            self.turning_speed = new_turning_speed

    def set_acceleration(self, new_acceleration):
        self.acceleration = new_acceleration if not self.is_moving_back else -new_acceleration

    def update(self):
        if self.acceleration:
            self.speed += self.acceleration
        self.move(change_x_by=self.turning_speed,
                  change_y_by=-(self.speed - self.player_speed) if self.player_speed is not None else 0)
        if self.rect.y - 1 < self.y_range[0] and self.speed >= self.player_speed or self.rect.y - 1 > self.y_range[1]:
            self.kill()

    def update_player_speed_data(self, new_player_speed):
        self.player_speed = new_player_speed

    def stop(self):
        self.speed = 0
        self.acceleration = 0
        self.turning_speed = 0


