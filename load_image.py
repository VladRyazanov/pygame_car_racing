import os
import pygame

pygame.init()


def load_image(name, color_key=None, flip_image=False, scale=1.0):
    # Модифицированная функция из уроков для загрузки изображения
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        raise SystemExit(message)

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)

    image = pygame.transform.rotozoom(image, 0, scale)
    if flip_image:
        image = pygame.transform.rotate(image, 180)
    return image
