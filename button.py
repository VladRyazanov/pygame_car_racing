import pygame

from load_image import load_image


class UsualButton(pygame.sprite.Sprite):
    """
    Класс обычной кнопки (в виде прямоугольника с текстом)
    """
    def __init__(self, button_group, x, y, width, height, text, function):

        super().__init__(button_group)

        # создание изображения, оно будет нужно для заливки цветом
        self.image = pygame.Surface([width, height])
        self.rect = pygame.Rect(x, y, width, height)

        font = pygame.font.SysFont('Arial', 30)
        self.text = font.render(text, True, (0, 0, 0))

        self.function = function

        self.colors = {
            'usual': '#555555',
            'covered': "#777777",
            'pressed': '#ffffff',
        }

    def was_covered(self):
        # функция, которая вызывается при наведении курсора на кнопку
        self.image.fill(self.colors["covered"])
        self.blit_text()

    def was_clicked(self):
        # функция, которая вызывается при нажатии на кнопку
        self.image.fill(self.colors["pressed"])
        self.blit_text()
        self.function()

    def was_released(self):
        # функция, которая вызывается при отпускании кнопки
        self.image.fill(self.colors["usual"])
        self.blit_text()

    def blit_text(self):
        # функция наложения текста на кнопку
        self.image.blit(self.text, (
            self.rect.width / 2 - self.text.get_width() / 2, self.rect.height / 2 - self.text.get_height() / 2))


class SelectCarCarButton(pygame.sprite.Sprite):
    """
    Класс кнопки для выбора автомобиля, сущности данного класса представляют собой кнопку с изображением автомобиля
    """
    def __init__(self, button_group, image_file_name, x, y, scale=1.0):
        super().__init__(button_group)
        self.group = button_group
        self.image_file_name = image_file_name
        self.x = x
        self.y = y
        # При выборе данной кнопки происходит ее сдвиг вверх, свойство self.previous_y сохраняет исходную координату
        self.previous_y = None
        self.scale = scale

        # rect и image сначала не имеют значений, их инициализация происходит в методе set_image_and_rect.
        # Это сделано для того, чтобы изображение кнопки могло легко изменяться (например, сдвигаться вверх)
        # при выборе и возвращаться к исходному
        self.rect = None
        self.image = None

        self.set_image_and_rect()

    def set_image_and_rect(self):
        self.image = load_image(self.image_file_name, scale=self.scale)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def become_selected(self):
        # данное условие проверяет, является ли машина выбранной,
        # на это указывает наличие значения у переменной исходного положения
        if self.previous_y is None:
            self.previous_y = self.y
            self.y -= 60
            self.set_image_and_rect()
            self.group.car_was_selected(self)

    def stop_being_selected(self):
        # если кнопка выбрана
        if self.previous_y is not None:
            self.y = self.previous_y
            self.previous_y = None
            self.set_image_and_rect()

    def was_clicked(self):
        self.become_selected()

    def was_released(self):
        # данный метод был добавлен для того, чтобы кнопками этого класса могли управлять группы кнопок,
        # унаследованные от ButtonGroup - класса, сущности которого управляют UsualButton-кнопками,
        # т.е для одинакового синтаксиса с UsualButton
        pass

    def was_covered(self):
        # причина добавления данного метода аналогична с was_released. При желании в этом методе можно добавить код,
        # который, например, будет изменять изображение кнопки при касании
        pass
