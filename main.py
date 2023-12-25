import pygame
import random
from sprite_group import SpriteGroup
from cars import BotCar, UserCar
from road_modes import TwoLanesForwardTwoLanesBackMode
from road_marking import RoadMarking

GAME_MODE = TwoLanesForwardTwoLanesBackMode()
FPS = 50
SCREEN_HEIGHT = 600
CARS_COUNT = 1

USER_CAR_IMAGE_FILE_NAME = "car3.png"
USER_MAX_SPEED = 10
USER_MAX_ACCELERATION = 0.5
USER_MAX_DECELERATION = 1

BOT_MAX_SPEED = 3
BOT_MAX_ACCELERATION = 0.2
BOT_MAX_DECELERATION = 0.5

ROAD_MARKING_WIDTH = 10
ROAD_MARKING_HEIGHT = 100
SPACE_BETWEEN_ROAD_MARKINGS = 200

pygame.init()
screen_size = GAME_MODE.screen_width, SCREEN_HEIGHT
screen = pygame.display.set_mode(screen_size)
all_sprites_group = SpriteGroup()
bot_cars_group = SpriteGroup()
all_cars_group = SpriteGroup()
road_markings_group = SpriteGroup()

user_car = UserCar(group=[all_sprites_group, all_cars_group],
                   image_file_name="car1.png",
                   max_acceleration=USER_MAX_ACCELERATION,
                   max_speed=USER_MAX_SPEED, max_deceleration=USER_MAX_DECELERATION, player_speed=None, x=GAME_MODE.get_player_x_coord(), y=SCREEN_HEIGHT // 2,
                   x_range=GAME_MODE.range_x, y_range=(0, SCREEN_HEIGHT), bot_cars_group=bot_cars_group)

clock = pygame.time.Clock()
distance_left_to_the_next_road_marking = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                user_car.gas_pressed()
            if event.key == pygame.K_DOWN:
                user_car.brake_pressed()
            if event.key == pygame.K_LEFT:
                user_car.turn_left()
            if event.key == pygame.K_RIGHT:
                user_car.turn_right()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                user_car.gas_released()
            else:
                user_car.turning_speed = 0
    screen.fill(pygame.Color("grey"))
    road_markings_group.draw(screen)
    all_cars_group.draw(screen)
    all_sprites_group.update()
    all_sprites_group.update_player_speed_data(new_player_speed=user_car.speed)
    clock.tick(FPS)
    pygame.display.flip()
    for i in range(CARS_COUNT - len(bot_cars_group)):
        new_bot_car = BotCar(group=[all_sprites_group, bot_cars_group, all_cars_group],
                         image_file_name=f"car{random.randrange(2, 11)}.png",
                         max_acceleration=BOT_MAX_ACCELERATION,
                         max_speed=BOT_MAX_SPEED, max_deceleration=BOT_MAX_DECELERATION, player_speed=0, x=GAME_MODE.cars_coords_x[random.randrange(4)],
                         y=0,
                         x_range=GAME_MODE.range_x, y_range=(0, SCREEN_HEIGHT), bot_cars_group=bot_cars_group, all_cars_group=all_cars_group)
        if new_bot_car.speed > user_car.speed:
            new_bot_car.move(y=SCREEN_HEIGHT)
        else:
            new_bot_car.move(y=new_bot_car.y_range[0])

    distance_left_to_the_next_road_marking -= user_car.speed
    if distance_left_to_the_next_road_marking <= 0:
        distance_left_to_the_next_road_marking = SPACE_BETWEEN_ROAD_MARKINGS
        for road_marking_x in GAME_MODE.road_marking_coords_x:
            new_road_marking = RoadMarking([all_sprites_group, road_markings_group], ROAD_MARKING_WIDTH, ROAD_MARKING_HEIGHT, road_marking_x,
                                           -ROAD_MARKING_HEIGHT, [0, SCREEN_HEIGHT], player_speed=user_car.speed)

pygame.quit()




