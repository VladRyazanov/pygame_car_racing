import pygame

from object import Object


class Car(Object):
    """Класс спрайта-машины, унаследован от класса Object"""
    def __init__(self, group, x, y, image_file_name, x_range, y_range, max_speed, max_acceleration, max_deceleration,
                 max_turning_speed,
                 player_speed, bot_cars_group, is_moving_back=False):
        super().__init__(group, x, y, image_file_name, x_range, y_range, player_speed, is_moving_back)
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.max_turning_speed = max_turning_speed
        # одним из свойств сущностей этого класса является группа машин-ботов.
        # Она будет нужна при проверке на столкновение
        self.bot_cars_group = bot_cars_group
        # Свойство, указывающее на то, что данная машина движется навстречу пользователю
        self.is_moving_back = is_moving_back

    def calculate_acceleration(self):
        # Данная функция считает максимальное ускорение при данной скорости.
        # Чем больше скорость, тем медленнее ускоряется автомобиль
        percentage_of_max_speed = abs(self.speed / self.max_speed)
        acceleration = self.max_acceleration * (1 - percentage_of_max_speed)
        return acceleration

    def update(self):
        super().update()
        self.speed = max(0, min(self.speed, self.max_speed)) \
            if not self.is_moving_back else min(0, max(self.speed, -self.max_speed))


class UserCar(Car):
    """
    Класс пользовательского автомобиля
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gas_is_pressed = False

    def gas_pressed(self):
        self.gas_is_pressed = True

    def brake_pressed(self):
        self.acceleration = -self.max_deceleration

    def gas_released(self):
        self.gas_is_pressed = False
        self.acceleration = -self.max_acceleration / 10

    def turn_right(self):
        super().set_turning_speed(self.max_turning_speed)

    def turn_left(self):
        super().set_turning_speed(-self.max_turning_speed)

    def update(self):
        super().update()
        if self.gas_is_pressed:
            self.acceleration = self.calculate_acceleration()
        # проверка на столкновение
        if any(map(lambda bot_car: pygame.sprite.collide_mask(self, bot_car), self.bot_cars_group)):
            for i in self.groups():
                i.game_over()


class BotCar(Car):
    """
    Класс машины-бота
    """
    def __init__(self, *args, all_cars_group, time_to_change_traffic_lane, game_mode, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_mode = game_mode
        self.all_cars_group = all_cars_group
        self.traffic_lanes_coords = self.game_mode.forward_cars_coords_x
        if self.is_moving_back:
            self.traffic_lanes_coords = self.game_mode.back_cars_coords_x
        # время, за которое бот должен менять полосу (если спереди препятствие)
        self.time_to_change_traffic_lane = time_to_change_traffic_lane
        self.some_car_is_forward_and_close = False
        self.new_traffic_lane_coords = None
        self.previous_speed = None
        self.previous_acceleration = None

    def dont_crash_into_other_car(self, other_car_speed):
        # метод, который вызывается при возникновении препятствий спереди (например, более медленной машины)
        if self.previous_speed is None:
            self.save_current_speed_and_acceleration_to_previous()
        self.speed = other_car_speed
        self.acceleration = 0
        # если бот еще не меняет полосу
        if self.new_traffic_lane_coords is None:
            self.try_change_traffic_lane()

    def save_current_speed_and_acceleration_to_previous(self):
        # Сохранение текущей скорости. Вызывается при возникновении препятствия,
        # чтобы возобновить скорость после его объезда
        self.previous_speed = self.speed
        self.previous_acceleration = self.acceleration

    def recover_previous_speed_and_acceleration(self):
        # Возобновление предыдущей скорости
        if self.previous_speed is not None:
            self.speed = self.previous_speed
            self.acceleration = self.previous_acceleration
            self.previous_speed = None
            self.previous_acceleration = None

    def check_if_some_car_is_forward_and_close(self):
        # Метод проверяет дорогу впереди бота на наличие препятствий
        x_range = range(self.rect.left, self.rect.right)
        for other_car in self.all_cars_group:
            if other_car is not self and not (isinstance(self, PoliceCar) and isinstance(other_car, UserCar)):
                if other_car.rect.left in x_range or other_car.rect.right in x_range:
                    # Данное условие проверяет, есть ли впереди машина с меньшей скоростью независимо от того,
                    # в какую сторону двигаются автомобили
                    if (self.rect.height >= self.rect.top - other_car.rect.bottom >= 0
                        and not self.is_moving_back and not other_car.is_moving_back
                        and self.speed >= other_car.speed) or (
                            self.rect.height > other_car.rect.top - self.rect.bottom > 0
                            and self.is_moving_back
                            and other_car.is_moving_back and self.speed < other_car.speed):
                        self.dont_crash_into_other_car(other_car.speed)
                        self.some_car_is_forward_and_close = True
                        break
        else:
            self.some_car_is_forward_and_close = False

    def check_if_some_car_prevents_turning(self, range_x_to_check):
        # Проверка на помехи при смене полосы. Вызывается перед тем, как бот решил перестроиться
        return any(map(lambda car: (car is not self and not (isinstance(self, PoliceCar) and isinstance(car, UserCar))
                                    and (car.rect.x in range_x_to_check or car.rect.right in range_x_to_check)
                                    and (car.rect.top in range(self.rect.top,
                                                               self.rect.bottom) or car.rect.bottom in range(
                    self.rect.top,
                    self.rect.bottom))), self.all_cars_group))

    def try_change_traffic_lane(self):
        # Метод, который пытается сменить дорожную полосу
        possible_traffic_lanes_coords = [i for i in self.traffic_lanes_coords if
                                         not self.rect.x == i and abs(
                                             self.rect.x - i) <= self.game_mode.traffic_lane_width]

        if possible_traffic_lanes_coords:
            if not self.is_moving_back:
                available_traffic_lanes_coords = list()
                for lane_coord in possible_traffic_lanes_coords:
                    for car in self.all_cars_group:
                        if self.check_if_some_car_prevents_turning(
                                range(lane_coord, lane_coord + self.game_mode.traffic_lane_width)):
                            break
                    else:
                        available_traffic_lanes_coords.append(lane_coord)
                if available_traffic_lanes_coords:
                    self.new_traffic_lane_coords = sorted(available_traffic_lanes_coords, key=lambda lane_coords: (
                        any(map(lambda car: car.rect.x in range(lane_coords,
                                                                lane_coords + self.game_mode.traffic_lane_width),
                                self.all_cars_group)),
                        max([abs(car.rect.x - self.rect.x) for car in self.all_cars_group if
                             car.rect.x in range(lane_coords, lane_coords + self.game_mode.traffic_lane_width)]) if [
                            abs(car.rect.x - self.rect.x) for car in self.all_cars_group if
                            car.rect.x in range(lane_coords, lane_coords + self.game_mode.traffic_lane_width)] else -1),
                                                          )[0]

                    self.set_turning_speed(
                        (self.new_traffic_lane_coords - self.rect.x) / self.time_to_change_traffic_lane)

    def update(self):
        super().update()
        self.check_if_some_car_is_forward_and_close()
        # Если бот менял полосу и уже сменил
        # self.rect.x // 2 == self.new_traffic_lane_coords // 2 - Деление цели и текущей координаты на 2 сделано потому,
        # что значение скорости смены полосы - обычно нецелое число,
        # а число пикселей на экране - целое. Из-за этого (из-за округления координат библиотекой pygame)
        # даже при верных значениях координат и скорости прибытие машины в цель не происходит
        if self.new_traffic_lane_coords is not None and self.rect.x // 2 == self.new_traffic_lane_coords // 2:
            self.rect.x = self.new_traffic_lane_coords
            self.new_traffic_lane_coords = None
            self.set_turning_speed(0)
            self.recover_previous_speed_and_acceleration()


class PoliceCar(BotCar):
    """
    Класс полицейской машины
    """
    def __init__(self, *args, user_car, **kwargs):
        super().__init__(args, **kwargs)
        self.user_car = user_car
        self.is_following_user = False
        self.acceleration = self.max_acceleration
        self.speed = 0
        # Смена значения self.traffic_lanes_coords происходит для того,
        # чтобы полицейская машина могла ехать по встречной полосе
        self.traffic_lanes_coords = self.game_mode.back_cars_coords_x + self.game_mode.forward_cars_coords_x

    def follow_user(self):
        self.is_following_user = True

    def try_to_get_closer_to_user_car(self):
        # Метод для того, чтобы полицейская машина пыталась приблизиться к пользователю
        coords_changing = self.max_turning_speed if self.rect.x < self.user_car.rect.x else -self.max_turning_speed
        if not self.check_if_some_car_prevents_turning(range(self.rect.x + coords_changing,
                                                             self.rect.x + coords_changing + self.rect.width)) \
                and not self.new_traffic_lane_coords:
            self.rect.x += coords_changing
        # если полицейская машина случайно обогнала пользователя
        if self.rect.top < self.user_car.rect.top:
            self.save_current_speed_and_acceleration_to_previous()
            self.acceleration = 0
            self.speed = self.user_car.speed
            self.new_traffic_lane_coords = None
        elif self.new_traffic_lane_coords is None and not self.some_car_is_forward_and_close:
            self.recover_previous_speed_and_acceleration()

    def update(self):
        super().update()
        if self.is_following_user:
            self.try_to_get_closer_to_user_car()
            # если полиция догнала пользователя
            if pygame.sprite.collide_mask(self, self.user_car):
                for i in self.groups():
                    i.game_over()
