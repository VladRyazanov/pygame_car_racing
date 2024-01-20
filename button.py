import pygame
from load_image import load_image


class UsualButton(pygame.sprite.Sprite):
    def __init__(self, button_group, x, y, width, height, text, function):
        super().__init__(button_group)

        self.image = pygame.Surface([width, height])
        self.rect = pygame.Rect(x, y, width, height)

        font = pygame.font.SysFont('Arial', 40)
        self.text = font.render(text, True, (0, 0, 0))

        self.function = function

        self.colors = {
            'usual': '#555555',
            'covered': "#777777",
            'pressed': '#ffffff',
        }

    def was_covered(self):
        self.image.fill(self.colors["covered"])
        self.blit_text()

    def was_clicked(self):
        self.image.fill(self.colors["pressed"])
        self.blit_text()
        self.function()

    def was_released(self):
        self.image.fill(self.colors["usual"])
        self.blit_text()

    def blit_text(self):
        self.image.blit(self.text, (
            self.rect.width / 2 - self.text.get_width() / 2, self.rect.height / 2 - self.text.get_height() / 2))


class SelectCarCarButton(pygame.sprite.Sprite):
    def __init__(self, button_group, image_file_name, x, y, scale=1.0):
        super().__init__(button_group)
        self.group = button_group
        self.image_file_name = image_file_name
        self.x = x
        self.y = y
        self.scale = scale

        self.rect = None
        self.image = None

        self.set_image_and_rect()

    def set_image_and_rect(self):
        self.image = load_image(self.image_file_name, scale=self.scale)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def become_selected(self):
        self.scale = 1.0
        self.set_image_and_rect()
        self.group.car_was_selected(self)

    def stop_being_selected(self):
        self.scale = 0.7
        self.set_image_and_rect()

    def was_clicked(self):
        self.become_selected()

    def was_released(self):
        pass

    def was_covered(self):
        pass

