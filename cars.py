import pygame

from object import Object
import random


class Car(Object):
    def __init__(self, group, x, y, image_file_name, x_range, y_range, max_speed, max_acceleration, max_deceleration, player_speed, bot_cars_group, is_moving_back=False):
        super().__init__(group, x, y, image_file_name, x_range, y_range, player_speed)
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.bot_cars_group = bot_cars_group
        self.is_moving_back = False
        if len([sprite for sprite in self.bot_cars_group if pygame.sprite.collide_mask(self, sprite)]) > 1:
            print("collide", len(bot_cars_group))
            self.kill()
            print("killed", len(bot_cars_group))

    def calculate_acceleration(self):
        percentage_of_max_speed = abs(self.speed / self.max_speed)
        acceleration = self.max_acceleration * (1 - percentage_of_max_speed)
        return acceleration

    def update(self):
        super().update()
        self.speed = max(0, min(self.speed, self.max_speed))


class UserCar(Car):
    def gas_pressed(self):
        self.acceleration = self.calculate_acceleration()

    def brake_pressed(self):
        self.acceleration = -self.max_deceleration
        print("pressed")

    def gas_released(self):
        self.acceleration = -self.max_acceleration / 10

    def turn_right(self):
        super().set_turning_speed(5)

    def turn_left(self):
        super().set_turning_speed(-5)

    def update(self):
        super().update()
        if any(map(lambda bot_car: pygame.sprite.collide_mask(self, bot_car), self.bot_cars_group)):
            self.groups()[0].game_over()
            print("GAME OVER")


class BotCar(Car):
    def __init__(self, *args, all_cars_group, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_cars_group = all_cars_group
        self.speed = random.randrange(self.max_speed * 3, self.max_speed * 10) / 10
        if random.randrange(2) == 1:
            self.acceleration = self.calculate_acceleration()

    def check_if_some_car_is_forward_and_close(self):
        x_range = range(self.rect.left, self.rect.right + 1)
        for other_car in self.all_cars_group:
            if other_car is not self:
                if other_car.rect.left in x_range or other_car.rect.right in x_range:
                    # если бот движется вперед, и машина на его полосе спереди (выше на экране)
                    if self.rect.top - max(other_car.rect.bottom, other_car.rect.top) >= 0 and not self.is_moving_back and self.speed > other_car.speed:
                        print("SOME CAR IS FORWARD")
                        self.speed = 0
                    # если бот движется по встречной для игрока полосе, и машина на его полосе спереди (ниже на экране)
                    elif self.rect.bottom - min(other_car.rect.bottom, other_car.rect.top) <= 0 and self.is_moving_back and self.speed > other_car.speed:
                        self.speed = other_car.speed

    def update(self):
        super().update()
        self.check_if_some_car_is_forward_and_close()





















