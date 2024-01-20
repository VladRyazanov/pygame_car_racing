import random
import sys

import pygame

from button_group import ButtonGroup, ChooseCarButtonGroup
from cars import BotCar, UserCar, PoliceCar
from road_marking import RoadMarking
from road_modes import FourLinesBackForLinesForwardMode, EightLinesForwardMode
from sprite_group import SpriteGroup

GAME_MODE = FourLinesBackForLinesForwardMode()
QUANTITY_OF_USERS = 1

FONT = pygame.font.SysFont('Arial', 40)

FPS = 120
SCREEN_WIDTH = GAME_MODE.screen_width
SCREEN_HEIGHT = 700
CARS_COUNT = 3

USER_CAR_IMAGE_FILE_NAME = "car1.png"
USER_MAX_SPEED = 15
USER_MAX_ACCELERATION = 0.03
USER_MAX_DECELERATION = 0.6
USER_MAX_TURNING_SPEED = 3

BOT_MAX_SPEED = 14
BOT_MAX_ACCELERATION = 0.03
BOT_MAX_DECELERATION = 0.5
BOT_MAX_TURNING_SPEED = 3

POLICE_CAR_MAX_SPEED = 13
POLICE_CAR_MAX_ACCELERATION = 0.04
POLICE_CAR_MAX_TURNING_SPEED = 1

ROAD_MARKING_WIDTH = GAME_MODE.road_marking_width
ROAD_MARKING_HEIGHT = 50
SPACE_BETWEEN_ROAD_MARKINGS = 100

TIME_FOR_BOTS_TO_CHANGE_TRAFFIC_LANE = 2
TIME_FOR_USER_CAR_TO_MOVE_UP_WHEN_POLICE_CHASE_STARTED = 1

SPEED_LIMIT = 100

KEYS_FOR_DRIVING = [{"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d},
                    {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT}]

pygame.init()
screen_size = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def handle_menu_screens(menu_buttons):
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


def menu_with_buttons(menu_buttons_names_and_functions, is_horizontal=False):
    menu_buttons = ButtonGroup(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, is_horizontal=is_horizontal)
    menu_buttons.set_buttons(menu_buttons_names_and_functions)
    handle_menu_screens(menu_buttons)


def menu_with_cars(buttons_file_names, selected_file_name, is_horizontal=False):
    menu_buttons = ChooseCarButtonGroup(x=SCREEN_WIDTH * 0.05, y=SCREEN_HEIGHT // 2 - 50,
                                        button_images_file_names=buttons_file_names,
                                        selected_file_name=selected_file_name, is_horizontal=is_horizontal,
                                        space_between_buttons=50)
    handle_menu_screens(menu_buttons)


def start_menu_window():
    menu_with_buttons({"Играть": lambda: choose_game_mode_window(), "Выбрать машину": choose_car_window})


def choose_quantity_of_players_window():
    menu_with_buttons({"Один игрок": lambda: set_quantity_of_users(1),
                       "Два игрока": lambda: set_quantity_of_users(2)})


def choose_game_mode_window():
    menu_with_buttons({"Без встречной полосы": lambda: set_game_mode(EightLinesForwardMode()),
                       "Со встречной полосой": lambda: set_game_mode(FourLinesBackForLinesForwardMode())})


def choose_car_window():
    menu_with_cars([f"car{i}.png" for i in range(1, 11)],
                   selected_file_name=USER_CAR_IMAGE_FILE_NAME,
                   is_horizontal=True)

def game_over():
    menu_with_buttons({"Начать заново": lambda: run_race(), "Главное меню": start_menu_window})


def run_race():
    all_sprites_group = SpriteGroup()
    bot_cars_group = SpriteGroup()
    all_cars_group = SpriteGroup()
    road_markings_group = SpriteGroup()

    police_car = None
    users_cars = list()

    for user in range(QUANTITY_OF_USERS):
        user_car = UserCar(group=[all_sprites_group, all_cars_group],
                           image_file_name=USER_CAR_IMAGE_FILE_NAME,
                           max_acceleration=USER_MAX_ACCELERATION,
                           max_speed=USER_MAX_SPEED, max_deceleration=USER_MAX_DECELERATION, player_speed=None,
                           x=GAME_MODE.get_player_x_coord() + user * GAME_MODE.traffic_lane_width,
                           y=SCREEN_HEIGHT * 0.8,
                           x_range=GAME_MODE.range_x, y_range=(0, SCREEN_HEIGHT),
                           bot_cars_group=bot_cars_group, max_turning_speed=USER_MAX_TURNING_SPEED)

        users_cars.append(user_car)

    if QUANTITY_OF_USERS == 2:
        for car in users_cars:
            car.set_acceleration(0.005)

    distance_left_to_the_next_road_marking = 0
    user_car_goal_pos = None
    user_car_moving_across_the_screen_speed = 0

    available_x_coords_for_car_creating_back_top = list()
    available_x_coords_for_car_creating_forward_top = list()

    def get_user_car_speed_in_kilometres_per_hour():
        return int(users_cars[0].speed * 10)

    def show_speed():
        speed_text = FONT.render(str(get_user_car_speed_in_kilometres_per_hour()), True,
                                 (0, 0, 0) if int(users_cars[0].speed * 10) < SPEED_LIMIT else (200, 0, 0))
        screen.blit(speed_text, (SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.05))

    def update_all_groups():
        all_sprites_group.update_player_speed_data(new_player_speed=users_cars[0].speed)
        all_sprites_group.update()
        all_cars_group.update()

    def draw_all_sprites():
        road_markings_group.draw(screen)
        all_cars_group.draw(screen)

    def move_user_down_when_police_chase_is_over():
        nonlocal user_car_goal_pos, user_car_moving_across_the_screen_speed
        user_car_goal_pos = SCREEN_HEIGHT * 0.8
        user_car_moving_across_the_screen_speed = (user_car_goal_pos - users_cars[
            0].rect.top) / (TIME_FOR_USER_CAR_TO_MOVE_UP_WHEN_POLICE_CHASE_STARTED * FPS)

    def move_user_car_up_so_police_car_will_be_visible():
        nonlocal user_car_goal_pos, user_car_moving_across_the_screen_speed
        user_car_goal_pos = SCREEN_HEIGHT * 0.5
        user_car_moving_across_the_screen_speed = (user_car_goal_pos - users_cars[
            0].rect.top) / (TIME_FOR_USER_CAR_TO_MOVE_UP_WHEN_POLICE_CHASE_STARTED * FPS)

    def create_police_car():
        nonlocal police_car

        police_car = PoliceCar([all_sprites_group, all_cars_group, bot_cars_group],
                                   image_file_name=USER_CAR_IMAGE_FILE_NAME,
                                   max_speed=POLICE_CAR_MAX_SPEED, max_acceleration=POLICE_CAR_MAX_ACCELERATION,
                                   max_deceleration=BOT_MAX_DECELERATION, player_speed=users_cars[0].speed,
                                   x=GAME_MODE.get_player_x_coord(), y_range=(0, SCREEN_HEIGHT),
                                   bot_cars_group=bot_cars_group,
                                   max_turning_speed=POLICE_CAR_MAX_TURNING_SPEED,
                                   user_car=users_cars[0], all_cars_group=all_cars_group,
                                   time_to_change_traffic_lane=TIME_FOR_BOTS_TO_CHANGE_TRAFFIC_LANE * FPS,
                                   game_mode=GAME_MODE,
                                   y=SCREEN_HEIGHT, x_range=GAME_MODE.range_x)
        police_car.set_speed(users_cars[0].speed)
        move_user_car_up_so_police_car_will_be_visible()
        police_car.follow_user()
        print("police_car_created")

    def update_available_x_coords_for_placing_cars():
        nonlocal available_x_coords_for_car_creating_forward_top
        nonlocal available_x_coords_for_car_creating_back_top

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

        available_x_coords_for_car_creating_forward_top = \
            [x for x in GAME_MODE.forward_cars_coords_x
             if not any(map(lambda car:
                            check_if_car_is_on_traffic_lane(car,
                                                            x,
                                                            GAME_MODE.traffic_lane_width)
                            and check_if_car_y_is_in_car_creating_place(
                                car), bot_cars_group))]

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
                for car_number in range(len(users_cars)):
                    if QUANTITY_OF_USERS == 1:
                        if event.key == KEYS_FOR_DRIVING[car_number]["up"]:
                            users_cars[car_number].gas_pressed()
                            print("gas pressed")
                        if event.key == KEYS_FOR_DRIVING[car_number]["down"]:
                            users_cars[car_number].brake_pressed()
                    if event.key == KEYS_FOR_DRIVING[car_number]["left"]:
                        users_cars[car_number].turn_left()
                    if event.key == KEYS_FOR_DRIVING[car_number]["right"]:
                        users_cars[car_number].turn_right()

            if event.type == pygame.KEYUP:
                for car_number in range(len(users_cars)):
                    if QUANTITY_OF_USERS == 1:
                        if event.key == KEYS_FOR_DRIVING[car_number]["up"] \
                                or event.key == KEYS_FOR_DRIVING[car_number]["down"]:
                            users_cars[car_number].gas_released()

                    if event.key == KEYS_FOR_DRIVING[car_number]["left"] \
                            or event.key == KEYS_FOR_DRIVING[car_number]["right"]:
                        users_cars[car_number].turning_speed = 0

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
                    new_bot_car.set_speed(random.randrange(max(BOT_MAX_SPEED // 2, 1),
                                                           max(BOT_MAX_SPEED // 2,
                                                               min(BOT_MAX_SPEED,
                                                                   int(users_cars[0].speed))) + 1))

                else:
                    new_bot_car.set_speed(random.randrange(max(BOT_MAX_SPEED // 2, 1), BOT_MAX_SPEED + 1))
                new_bot_car.set_acceleration(random.randrange(0, int(BOT_MAX_ACCELERATION * 10) + 1) / 10)

        distance_left_to_the_next_road_marking -= users_cars[0].speed
        if distance_left_to_the_next_road_marking <= 0:
            distance_left_to_the_next_road_marking = SPACE_BETWEEN_ROAD_MARKINGS
            for road_marking_x in GAME_MODE.road_marking_coords_x:
                new_road_marking = RoadMarking([all_sprites_group, road_markings_group], ROAD_MARKING_WIDTH,
                                               ROAD_MARKING_HEIGHT, road_marking_x,
                                               -ROAD_MARKING_HEIGHT, [0, SCREEN_HEIGHT],
                                               player_speed=users_cars[0].speed)


        if QUANTITY_OF_USERS == 1:
            if get_user_car_speed_in_kilometres_per_hour() > SPEED_LIMIT * 1.15 and not police_car:
                create_police_car()
            if user_car_goal_pos is not None:
                users_cars[0].move(change_y_by=user_car_moving_across_the_screen_speed)
                if user_car_goal_pos // 2 == users_cars[0].rect.top // 2:
                    user_car_goal_pos = None
                    user_car_moving_across_the_screen_speed = None
                print("user_car_moved")


        print(police_car)
        screen.fill(pygame.Color("grey"))
        update_all_groups()
        draw_all_sprites()
        show_speed()
        clock.tick(FPS)
        pygame.display.flip()

    game_over()


start_menu_window()
