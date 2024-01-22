import pygame

from button import UsualButton, SelectCarCarButton


class ButtonGroup(pygame.sprite.Group):
    """
    Класс группы кнопок, объекты которого располагают кнопки, отслеживают их нажатия и состояния
    """

    def __init__(self, x, y, space_between_buttons=25, is_horizontal=False):
        super().__init__()
        # эта переменная следит за тем, чтобы нажать кнопку можно было только после того,
        # как мышь была отпущена после прошлого нажатия
        # Это сделано для того, не было багов при нажатии на кнопки, после которых на экране должны появиться
        # другие кнопки, например, пользователь нажимает кнопку "Играть" в главном меню игры,
        # и после этого появляется новое меню. Если не отслеживать отпускание мыши,
        #  то кнопка второго меню будет случайно нажата
        self.can_click_button = False
        self.is_horizontal = is_horizontal
        self.x = x
        self.y = y
        self.space_between_buttons = space_between_buttons

    def set_buttons(self, buttons_texts_and_functions, buttons_width=350, buttons_height=100):
        # создание и размещение кнопок было выведено в отдельную функцию для того,
        # чтобы ChooseCarButtonGroup мог наследоваться от этого класса
        current_button_coord = self.y if not self.is_horizontal else self.x
        for button_text in buttons_texts_and_functions:
            new_button = UsualButton(self, self.x if not self.is_horizontal else current_button_coord,
                                     self.y if self.is_horizontal else current_button_coord,
                                     buttons_width, buttons_height, button_text,
                                     buttons_texts_and_functions[button_text])
            current_button_coord += self.space_between_buttons + buttons_height if not self.is_horizontal \
                else buttons_width

    def update(self):
        # Метод для отслеживания нажатий на кнопки, касаний кнопок и т.д
        super().update()
        current_mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed(3)[0]
        if not mouse_clicked:
            self.can_click_button = True
        for button in self.sprites():
            if current_mouse_pos[0] in range(button.rect.left, button.rect.right) \
                    and current_mouse_pos[1] in range(button.rect.top, button.rect.bottom):
                if mouse_clicked and self.can_click_button:
                    button.was_clicked()
                    self.can_click_button = False
                    continue
                button.was_covered()
            else:
                button.was_released()


class ChooseCarButtonGroup(ButtonGroup):
    """
    Класс группы кнопок для выбора автомобиля, унаследован от группы обычных кнопок
    """
    def __init__(self, *args, button_images_file_names, selected_file_name, function, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_file_name = selected_file_name
        self.function = function
        self.ready_button = None
        self.set_buttons(button_images_file_names)

    def set_buttons(self, button_images):
        # метод для создания и расположения кнопок. В качестве параметра button_images
        # передается список из названий файлов - изображений автомобилей
        current_button_coord = self.y if not self.is_horizontal else self.x
        for button_image_file_name in button_images:
            new_button = SelectCarCarButton(self, button_image_file_name,
                                            self.x if not self.is_horizontal else current_button_coord,
                                            self.y if self.is_horizontal else current_button_coord)
            current_button_coord += self.space_between_buttons + new_button.rect.height if not self.is_horizontal \
                else new_button.rect.width
        self.ready_button = UsualButton(self, self.x + 150 if not self.is_horizontal else self.x,
                                        self.y if not self.is_horizontal else self.y + 150,
                                        400, 100, "Готово",
                                        function=lambda: self.function(self.get_selected_car_image_file_name()))
        #  цикл для поиска и автоматического нажатия выбранной на данный момент кнопки
        for button in self.sprites():
            if button is not self.ready_button and button.image_file_name == self.selected_file_name:
                button.become_selected()
                break

    def car_was_selected(self, car):
        # метод, который вызывается при выборе автомобиля. Он делает все остальные кнопки невыбранными и сохраняет выбор
        self.selected_file_name = car.image_file_name
        for button in self.sprites():
            if button is not self.ready_button and button.image_file_name != self.selected_file_name:
                button.stop_being_selected()

    def get_selected_car_image_file_name(self):
        return self.selected_file_name
