import pygame

class UI:

    def __init__(self, width, height, fill):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.rect = self.surface.get_rect()
        self.surface.fill(fill)

class Window(UI):

    def __init__(self, width, height, fill=(255, 255, 255)):
        super(Window, self).__init__(width, height, fill)
        self.buttons = {}

    def add_buttons(self, buttons):
        for b in buttons:
            self.add_button(b)

    def add_button(self, button):
        """ Adds button object to list of buttons """
        # Add it only if it isn't already in the list
        if button.name not in self.buttons:
            self.buttons[button.name] = button

    def fill(self, fill):
        """ fills window with specified color """
        self.surface.fill(fill)

    def click_button(self, mouse_click_pos):
        """ returns button that has been clicked """
        for name, button in self.buttons.items():
            if button.rect.collidepoint(mouse_click_pos):
                return button

    def set_position(self, position):
        """ sets the position of the topleft corner """
        self.rect.topleft = position

    def draw(self, surface):
        """ draws the window onto the specified surface """
        surface.blit(self.surface, self.rect.topleft)
        for name, button in self.buttons.items():
            button.draw(surface)

class Button(UI):

    def __init__(self, name, width, height, fill=(255, 255, 255)):
        super(Button, self).__init__(width, height, fill)
        self.name = name

    def set_text(self, arg):
        """ assigns the button a text object """
        if isinstance(arg, str):
            font = pygame.font.SysFont(None, 25)
            text_surf = font.render(arg, True, BLACK)

    def set_position(self, position):
        """ sets the position of the topleft corner """
        self.rect.topleft = position

    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)
