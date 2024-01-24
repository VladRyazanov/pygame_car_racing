import random
import sys

import pygame

from button_group import ButtonGroup, ChooseCarButtonGroup
from cars import BotCar, UserCar, PoliceCar
from road_marking import RoadMarking
from road_modes import FourLinesBackForLinesForwardMode, EightLinesForwardMode
from sidewalk_object import SidewalkObject
from sprite_group import SpriteGroup

# Инициализация режима игры, по умолчанию - четыре полосы в каждую сторону
GAME_MODE = FourLinesBackForLinesForwardMode()
QUANTITY_OF_USERS = 1
SPEED_LIMIT = 110

# Названия изображений машин и их характеристики, не распространяются на ботов,
# ограничения по скорости, ускорению и т.д у всех ботов одни
CAR_IMAGES_AND_SPEEDS = {
    "car1.png": {"max_speed": 11, "max_acceleration": 0.02, "max_turning_speed": 2, "max_deceleration": 0.1},
    "car2.png": {"max_speed": 12, "max_acceleration": 0.025, "max_turning_speed": 1.5, "max_deceleration": 0.15},
    "car3.png": {"max_speed": 13, "max_acceleration": 0.027, "max_turning_speed": 2, "max_deceleration": 0.17},
    "car4.png": {"max_speed": 14, "max_acceleration": 0.028, "max_turning_speed": 1.5, "max_deceleration": 0.2},
    "car5.png": {"max_speed": 15, "max_acceleration": 0.03, "max_turning_speed": 2.5, "max_deceleration": 0.26},
    "car6.png": {"max_speed": 16, "max_acceleration": 0.031, "max_turning_speed": 2.2, "max_deceleration": 0.28},
    "car7.png": {"max_speed": 19, "max_acceleration": 0.045, "max_turning_speed": 2.7, "max_deceleration": 0.3},
    "car8.png": {"max_speed": 20, "max_acceleration": 0.046, "max_turning_speed": 2.5, "max_deceleration": 0.4},
    "car9.png": {"max_speed": 23, "max_acceleration": 0.06, "max_turning_speed": 3, "max_deceleration": 0.5},
    "car10.png": {"max_speed": 24, "max_acceleration": 0.062, "max_turning_speed": 2.7, "max_deceleration": 0.5},
}

FONT = pygame.font.SysFont('Arial', 40)

FPS = 80
# Ширина экрана зависит от кол-ва полос и их ширины, поэтому этот параметр берется из режима игры
SCREEN_WIDTH = GAME_MODE.screen_width
SCREEN_HEIGHT = 700
CARS_COUNT = 3

# Характеристики машины пользователя по умолчанию, меняются при выборе другой машины
USER_CAR_IMAGE_FILE_NAME = "car1.png"
USER_MAX_SPEED = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_speed"]
USER_MAX_ACCELERATION = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_acceleration"]
USER_MAX_DECELERATION = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_deceleration"]
USER_MAX_TURNING_SPEED = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_turning_speed"]

# Характеристики ботов
BOT_MAX_SPEED = 13
BOT_MAX_ACCELERATION = 0.03
BOT_MAX_DECELERATION = 0.5
BOT_MAX_TURNING_SPEED = 3

# Часть характеристик полицейского автомобиля. Остальные характеристики задаются непосредственно перед погоней
# для приемлемого соотношения с текущей скоростью пользователя
POLICE_CAR_IMAGE_FILE_NAME = "police_car.png"
POLICE_CAR_MAX_TURNING_SPEED = 1

# Характеристики дорожной разметки и объектов по бокам от дороги
ROAD_MARKING_WIDTH = GAME_MODE.road_marking_width
ROAD_MARKING_HEIGHT = 50
SPACE_BETWEEN_ROAD_MARKINGS = 100
SPACE_BETWEEN_SIDEWALK_OBJECTS = 300


# Прочие характеристики
TIME_FOR_BOTS_TO_CHANGE_TRAFFIC_LANE = 2
TIME_FOR_USER_CAR_TO_MOVE_UP_WHEN_POLICE_CHASE_STARTED = 1

pygame.init()
screen_size = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()


def terminate():
    # Выход из игры
    pygame.quit()
    sys.exit()


def handle_menu_screens(menu_buttons):
    # Функция для обработки экранов с меню, на вход принимает группу кнопок
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color("grey"))
        menu_buttons.update()
        menu_buttons.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()

    terminate()


def set_game_mode(new_game_mode):
    global GAME_MODE
    GAME_MODE = new_game_mode
    choose_quantity_of_players_window()


def set_quantity_of_users(new_quantity):
    global QUANTITY_OF_USERS
    QUANTITY_OF_USERS = new_quantity
    run_race()


def set_user_car(user_car_image_file_name):
    global USER_CAR_IMAGE_FILE_NAME, USER_MAX_SPEED, USER_MAX_ACCELERATION, \
        USER_MAX_TURNING_SPEED, USER_MAX_DECELERATION

    USER_CAR_IMAGE_FILE_NAME = user_car_image_file_name
    USER_MAX_SPEED = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_speed"]
    USER_MAX_ACCELERATION = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_acceleration"]
    USER_MAX_DECELERATION = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_deceleration"]
    USER_MAX_TURNING_SPEED = CAR_IMAGES_AND_SPEEDS[USER_CAR_IMAGE_FILE_NAME]["max_turning_speed"]
    start_menu_window()


def menu_with_buttons(menu_buttons_names_and_functions, is_horizontal=False):
    # Универсальная функция для создания обычного меню
    menu_buttons = ButtonGroup(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, is_horizontal=is_horizontal)
    menu_buttons.set_buttons(menu_buttons_names_and_functions)
    handle_menu_screens(menu_buttons)


def menu_with_cars(buttons_file_names, selected_file_name, function, is_horizontal=False):
    # Функция для создания меню с машинами
    cars_menu_buttons = ChooseCarButtonGroup(x=SCREEN_WIDTH * 0.05, y=SCREEN_HEIGHT // 2 - 50,
                                             button_images_file_names=buttons_file_names,
                                             selected_file_name=selected_file_name, is_horizontal=is_horizontal,
                                             space_between_buttons=50, function=function)

    handle_menu_screens(cars_menu_buttons)


def start_menu_window():
    # стартовое меню
    menu_with_buttons({"Играть": lambda: choose_game_mode_window(), "Выбрать машину": choose_car_window})


def choose_quantity_of_players_window():
    # меню для выбора количества игроков
    menu_with_buttons({"Один игрок": lambda: set_quantity_of_users(1),
                       "Два игрока": lambda: set_quantity_of_users(2)})


def choose_game_mode_window():
    # меню для выбора режима игры
    menu_with_buttons({"Без встречной полосы": lambda: set_game_mode(EightLinesForwardMode()),
                       "Со встречной полосой": lambda: set_game_mode(FourLinesBackForLinesForwardMode())})


def choose_car_window():
    # меню для выбора машины
    menu_with_cars([f"car{i}.png" for i in range(1, 11)],
                   selected_file_name=USER_CAR_IMAGE_FILE_NAME,
                   is_horizontal=True, function=set_user_car)


def game_over():
    # меню после окончания игры
    menu_with_buttons({"Начать заново": lambda: run_race(), "Главное меню": start_menu_window})


def run_race():
    # Функция игры
    # Инициализация групп
    all_sprites_group = SpriteGroup()
    bot_cars_group = SpriteGroup()
    all_cars_group = SpriteGroup()
    road_markings_group = SpriteGroup()
    sidewalk_objects_group = SpriteGroup()

    # Полицейская машина создается непосредственно перед погоней, в остальное время police_car - None
    police_car = None
    users_cars = list()
    # Создание машин пользователей
    for user in range(QUANTITY_OF_USERS):
        user_car = UserCar(group=[all_sprites_group, all_cars_group],
                           image_file_name=USER_CAR_IMAGE_FILE_NAME if user != 1 else random.choice(
                               [i for i in CAR_IMAGES_AND_SPEEDS.keys() if i != USER_CAR_IMAGE_FILE_NAME]),
                           max_acceleration=USER_MAX_ACCELERATION,
                           max_speed=USER_MAX_SPEED, max_deceleration=USER_MAX_DECELERATION, player_speed=None,
                           x=GAME_MODE.get_player_x_coord() + user * GAME_MODE.traffic_lane_width,
                           y=SCREEN_HEIGHT * 0.8,
                           x_range=GAME_MODE.range_x, y_range=(0, SCREEN_HEIGHT),
                           bot_cars_group=bot_cars_group, max_turning_speed=USER_MAX_TURNING_SPEED)

        users_cars.append(user_car)

    # При игре вдвоем ускоряться и тормозить вручную нельзя, машины будут ускоряться самостоятельно
    if QUANTITY_OF_USERS == 2:
        for car in users_cars:
            car.set_acceleration(0.005)

    distance_left_to_the_next_road_marking = 0
    distance_left_to_the_next_sidewalk_object = 0
    # Параметры для сдвига машины пользователя во время погони
    user_car_goal_pos = None
    user_car_moving_across_the_screen_speed = 0

    # Списки координат для создания ботов
    available_x_coords_for_car_creating_back_top = list()
    available_x_coords_for_car_creating_forward_top = list()

    def get_user_car_speed_in_kilometres_per_hour():
        # Преобразование скорости пользователя в километры в час.
        # Нужно для отслеживания лимита скорости и отображения текущец скорости
        return int(users_cars[0].speed * 10)

    def show_speed():
        # отображение скорости
        speed_text = FONT.render(str(get_user_car_speed_in_kilometres_per_hour()), True,
                                 (0, 0, 0) if int(users_cars[0].speed * 10) < SPEED_LIMIT else (200, 0, 0))
        screen.blit(speed_text, (SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.05))

    def update_all_groups():
        # Обновление групп
        all_sprites_group.update_player_speed_data(new_player_speed=users_cars[0].speed)
        all_sprites_group.update()
        all_cars_group.update()

    def draw_all_sprites():
        # Отрисовка
        road_markings_group.draw(screen)
        all_cars_group.draw(screen)
        sidewalk_objects_group.draw(screen)

    def move_user_down_when_police_chase_is_over():
        # Сдвиг машины пользователя вниз после окончания погони
        nonlocal user_car_goal_pos, user_car_moving_across_the_screen_speed
        user_car_goal_pos = SCREEN_HEIGHT * 0.8
        user_car_moving_across_the_screen_speed = (user_car_goal_pos - users_cars[
            0].rect.top) / (TIME_FOR_USER_CAR_TO_MOVE_UP_WHEN_POLICE_CHASE_STARTED * FPS)

    def move_user_car_up_so_police_car_will_be_visible():
        # Сдвиг машины пользователя вверх перед погоней
        # Для того, чтобы машину полиции было видно
        nonlocal user_car_goal_pos, user_car_moving_across_the_screen_speed
        user_car_goal_pos = SCREEN_HEIGHT * 0.5
        user_car_moving_across_the_screen_speed = (user_car_goal_pos - users_cars[
            0].rect.top) / (TIME_FOR_USER_CAR_TO_MOVE_UP_WHEN_POLICE_CHASE_STARTED * FPS)

    def create_police_car():
        nonlocal police_car
        # Создание полицейской машины
        police_car = PoliceCar([all_sprites_group, all_cars_group, bot_cars_group],
                               image_file_name=POLICE_CAR_IMAGE_FILE_NAME,
                               max_speed=USER_MAX_SPEED * 0.95,
                               max_acceleration=USER_MAX_ACCELERATION,
                               max_deceleration=BOT_MAX_DECELERATION, player_speed=users_cars[0].speed,
                               x=users_cars[0].rect.x, y_range=(0, SCREEN_HEIGHT),
                               bot_cars_group=bot_cars_group,
                               max_turning_speed=POLICE_CAR_MAX_TURNING_SPEED,
                               user_car=users_cars[0], all_cars_group=all_cars_group,
                               time_to_change_traffic_lane=TIME_FOR_BOTS_TO_CHANGE_TRAFFIC_LANE * FPS,
                               game_mode=GAME_MODE,
                               y=SCREEN_HEIGHT, x_range=GAME_MODE.range_x)
        police_car.set_speed(users_cars[0].speed)
        move_user_car_up_so_police_car_will_be_visible()
        police_car.follow_user()

    def update_available_x_coords_for_placing_cars():
        nonlocal available_x_coords_for_car_creating_forward_top
        nonlocal available_x_coords_for_car_creating_back_top

        # Обновление координат для создания ботов

        def check_if_car_is_on_traffic_lane(car, traffic_lane_start_x, traffic_lane_width):
            if car.rect.left in range(traffic_lane_start_x,
                                      traffic_lane_start_x + traffic_lane_width) or car.rect.right \
                    in range(traffic_lane_start_x, traffic_lane_start_x + traffic_lane_width):
                return True
            return False

        def check_if_car_y_is_in_car_creating_place(car):
            if car.rect.top <= car.rect.height:
                return True
            return False

        # Запись координат, доступных для расположения машин на полосе пользователя
        available_x_coords_for_car_creating_forward_top = \
            [x for x in GAME_MODE.forward_cars_coords_x
             if not any(map(lambda car:
                            check_if_car_is_on_traffic_lane(car,
                                                            x,
                                                            GAME_MODE.traffic_lane_width)
                            and check_if_car_y_is_in_car_creating_place(
                                car), bot_cars_group))]
        # Запись координат, доступных для расположения машин на встречной полосе
        available_x_coords_for_car_creating_back_top \
            = [x for x in GAME_MODE.back_cars_coords_x
               if not any(map(lambda car: check_if_car_is_on_traffic_lane(car, x,
                                                                          GAME_MODE.traffic_lane_width)
                                          and check_if_car_y_is_in_car_creating_place(
                car), bot_cars_group))]

    running = True
    while not all_sprites_group.game_is_over and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if QUANTITY_OF_USERS == 1:
                    if event.key == pygame.K_w:
                        users_cars[0].gas_pressed()
                    if event.key == pygame.K_s:
                        users_cars[0].brake_pressed()
                if event.key == pygame.K_d:
                    users_cars[0].turn_right()
                if event.key == pygame.K_a:
                    users_cars[0].turn_left()
                if event.key == pygame.K_RIGHT:
                    users_cars[1].turn_right()
                if event.key == pygame.K_LEFT:
                    users_cars[0].turn_left()

            if event.type == pygame.KEYUP:
                if QUANTITY_OF_USERS == 1:
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        users_cars[0].gas_released()
                if event.key == pygame.K_d or event.key == pygame.K_a:
                    users_cars[0].set_turning_speed(0)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    users_cars[1].set_turning_speed(0)

        # если на экране машин-ботов меньше, чем нужно
        if len(bot_cars_group) < CARS_COUNT:
            update_available_x_coords_for_placing_cars()
            all_available_lists = [i for i in [available_x_coords_for_car_creating_forward_top,
                                               available_x_coords_for_car_creating_back_top] if i]
            if all_available_lists:
                random_list = random.choice(all_available_lists)
                random_x_coord = random.choice(random_list)
                new_bot_car = BotCar(group=[all_sprites_group, bot_cars_group, all_cars_group],
                                     image_file_name=f"car{random.randrange(1, 11)}.png",
                                     max_acceleration=BOT_MAX_ACCELERATION,
                                     max_speed=BOT_MAX_SPEED, max_deceleration=BOT_MAX_DECELERATION,
                                     player_speed=users_cars[0].speed, x=random_x_coord,
                                     y=0,
                                     x_range=GAME_MODE.range_x, y_range=(0, SCREEN_HEIGHT),
                                     bot_cars_group=bot_cars_group,
                                     all_cars_group=all_cars_group,
                                     is_moving_back=random_x_coord in available_x_coords_for_car_creating_back_top,
                                     game_mode=GAME_MODE,
                                     time_to_change_traffic_lane=TIME_FOR_BOTS_TO_CHANGE_TRAFFIC_LANE * FPS,
                                     max_turning_speed=BOT_MAX_TURNING_SPEED)

                new_bot_car.move(y=-new_bot_car.rect.height)
                if random_list is available_x_coords_for_car_creating_forward_top:
                    # при расположении машины на полосе пользователя сверху
                    # скорость созданной машины должна быть меньше, чем у пользователя
                    new_bot_car.set_speed(random.randrange(max(BOT_MAX_SPEED // 2, 1),
                                                           max(BOT_MAX_SPEED // 2,
                                                               min(BOT_MAX_SPEED,
                                                                   int(users_cars[0].speed))) + 1))

                else:
                    new_bot_car.set_speed(random.randrange(max(BOT_MAX_SPEED // 2, 1), BOT_MAX_SPEED + 1))

        # создание недостающих дорожных меток
        distance_left_to_the_next_road_marking -= users_cars[0].speed
        if distance_left_to_the_next_road_marking <= 0:
            distance_left_to_the_next_road_marking = SPACE_BETWEEN_ROAD_MARKINGS
            for road_marking_x in GAME_MODE.road_marking_coords_x:
                new_road_marking = RoadMarking([all_sprites_group, road_markings_group], ROAD_MARKING_WIDTH,
                                               ROAD_MARKING_HEIGHT, road_marking_x,
                                               -ROAD_MARKING_HEIGHT, [0, SCREEN_HEIGHT],
                                               player_speed=users_cars[0].speed)

        # создание недостающих объектов по бокам от дороги
        distance_left_to_the_next_sidewalk_object -= users_cars[0].speed
        if distance_left_to_the_next_sidewalk_object <= 0:
            distance_left_to_the_next_sidewalk_object = SPACE_BETWEEN_SIDEWALK_OBJECTS
            for i in range(2):
                new_sidewalk_object = SidewalkObject([sidewalk_objects_group, all_sprites_group],
                                                     50 if i == 0 else SCREEN_WIDTH,
                                                     -SPACE_BETWEEN_SIDEWALK_OBJECTS,
                                                     [0, SCREEN_HEIGHT], users_cars[0].speed)

        # превышение скорости отслеживается только когда игрок один, при игре вдвоем полицейская погоня невозможна
        if QUANTITY_OF_USERS == 1:
            if get_user_car_speed_in_kilometres_per_hour() > SPEED_LIMIT * 1.1 and not police_car:
                create_police_car()
            # если погоня началась/закончилась и происходит сдвиг пользовательской машины относительно экрана
            if user_car_goal_pos is not None:
                users_cars[0].move(change_y_by=user_car_moving_across_the_screen_speed)
                if user_car_goal_pos // 2 == users_cars[0].rect.top // 2:
                    user_car_goal_pos = None
                    user_car_moving_across_the_screen_speed = None
        # если пользователь оторвался от погони
        if police_car is not None and not police_car.groups():
            police_car = None
            move_user_down_when_police_chase_is_over()

        # отрисовка и обновление
        screen.fill(pygame.Color("grey"))
        pygame.draw.rect(screen, pygame.Color((0, 120, 0)), (0, 0, min(GAME_MODE.range_x), SCREEN_HEIGHT), 0)
        pygame.draw.rect(screen, pygame.Color((0, 120, 0)), (max(GAME_MODE.range_x), 0,
                                                             SCREEN_WIDTH - max(GAME_MODE.range_x), SCREEN_HEIGHT), 0)
        update_all_groups()
        draw_all_sprites()
        show_speed()
        clock.tick(FPS)
        pygame.display.flip()

    game_over()


start_menu_window()
