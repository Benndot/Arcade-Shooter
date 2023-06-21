import pygame
from pygame import mixer
import random
import math

pygame.init()


class Color:
    slategray = (112, 128, 144)
    lightgray = (165, 175, 185)
    blackish = (20, 20, 20)
    white = (255, 255, 255)
    lighter_blue = (0, 0, 255)
    darker_blue = (0, 0, 170)
    lighter_red = (255, 0, 0)
    thunderbird_red = (200, 15, 25)
    darker_red = (180, 0, 0)
    lighter_green = (0, 255, 0)
    darker_green = (0, 160, 0)
    thistle_green = (210, 210, 190)
    black = (0, 0, 0)


game_soundtrack = []


class MusicSettings:

    volume_level = 50
    music_paused = False
    current_track_index = 0
    tracklist = game_soundtrack

    def music_toggle(self):
        print("The music pausing bool has been toggled")
        self.music_paused = not self.music_paused
        if self.music_paused:
            mixer.music.pause()
        elif not self.music_paused:
            mixer.music.unpause()

    def change_music_volume(self, change_int: int):
        self.volume_level += change_int
        if self.volume_level > 100:
            self.volume_level = 100
        if self.volume_level < 0:
            self.volume_level = 0
        mixer.music.set_volume(self.volume_level / 350)

    def randomize_song(self):
        if self.tracklist:
            self.current_track_index = random.randint(0, len(self.tracklist)-1)
            print(f"Song index chosen: {self.current_track_index}")
            mixer.music.load(self.tracklist[self.current_track_index])
            mixer.music.set_volume(MusicSettings.volume_level / 300)
            mixer.music.play(-1)

    def cycle_track(self):
        mixer.music.stop()
        self.current_track_index += 1
        if self.current_track_index >= len(self.tracklist):
            self.current_track_index = 0
        mixer.music.load(self.tracklist[self.current_track_index])
        mixer.music.set_volume(self.volume_level / 300)
        mixer.music.play(-1)


class Screen:
    width = 1080
    height = 720
    screen = pygame.display.set_mode((width, height))

    def update_screen(self):
        self.screen = pygame.display.set_mode((self.width, self.height))

    def make_default(self):
        self.width = 1080
        self.height = 720
        self.update_screen()

    def make_large(self):
        self.width = 1600
        self.height = 900
        self.update_screen()

    def make_fullscreen(self):
        self.width = 1920
        self.height = 1080
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

    def cycle_screen_resize(self):
        if self.width == 1080:
            self.make_large()
        elif self.width == 1600:
            self.make_fullscreen()
        else:
            self.make_default()


class Font:
    xxl = pygame.font.SysFont("bahnschrift", math.ceil(Screen.height * 0.0695 * 1.4))
    xl = pygame.font.SysFont("bahnschrift", math.ceil(Screen.height * 0.0695 * 1.2))
    lg = pygame.font.SysFont("bahnschrift", math.ceil(Screen.height * 0.0695))
    med_lg = pygame.font.SysFont("bahnschrift", math.ceil(Screen.height * 0.0695 * 0.8))
    med = pygame.font.SysFont("bahnschrift", math.ceil(Screen.height * 0.0695 * 0.6))
    sml_med = pygame.font.SysFont("bahnschrift", math.ceil(Screen.height * 0.0695 * 0.45))
    sml = pygame.font.SysFont("bahnschrift", math.ceil(Screen.height * 0.0695 * 0.33))


# Utility functions for text and buttons ----------------------------------------------------------------------------

def create_onscreen_text(font_size, color, message, x, y, x_adjust: bool = False):

    text = font_size.render(message, True, color)

    if x_adjust:
        text_width = text.get_width()
        x = x - (text_width / 2)

    Screen.screen.blit(text, (x, y))


def create_title_text(message, font_size=Font.lg, color=(0, 0, 0), x=Screen.width / 2, y=Screen.height * 0.1):

    render_text = font_size.render(message, True, color)
    adjusted_x = (x - render_text.get_width()) / 2
    Screen.screen.blit(render_text, (adjusted_x, y))


def display_text_over_multiple_lines(text, font, line_character_limit, start_x, start_y, line_height_step):
    start_index = 0
    height_multiplier = 1
    index_counter = 0
    for index, char in enumerate(text):
        index_counter += 1
        if char == " " and index_counter >= line_character_limit:
            end_index = index + 1
            create_onscreen_text(font, (0, 0, 0), text[start_index: end_index], start_x, start_y * height_multiplier,
                                 False)
            height_multiplier += line_height_step
            start_index = index
            index_counter = 0
        if index >= len(text) - 1:
            create_onscreen_text(font, (0, 0, 0), text[start_index: -1], start_x, start_y * height_multiplier, False)
            break


def create_transparent_button(width, height, x, y):

    mouse = pygame.mouse.get_pos()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        s = pygame.Surface((width, height))  # the size of your rect
        s.set_alpha(128)  # alpha level
        s.fill((255, 255, 255))  # this fills the entire surface
        Screen.screen.blit(s, (x, y))  # (0,0) are the top-left coordinates
        for evnt in pygame.event.get():
            if evnt.type == pygame.MOUSEBUTTONUP:
                return True


def create_text_button(font_choice, msg: str, x: int or float, y: int or float,
                       text_color: tuple[int, int, int] = Color.black,
                       default_color: tuple[int, int, int] = Color.slategray,
                       hover_color: tuple[int, int, int] = Color.lightgray,
                       x_adjust: bool = False, click_sound: bool = True):

    mouse = pygame.mouse.get_pos()

    button_msg = font_choice.render(msg, True, text_color)

    button_width = button_msg.get_width() + (button_msg.get_width() * 0.20)
    button_height = button_msg.get_height() + (button_msg.get_height() * 0.20)

    if x_adjust:
        x = x - (button_width / 2)

    # The experimental version
    if x + button_width > mouse[0] > x and y + button_height > mouse[1] > y:
        pygame.draw.rect(Screen.screen, hover_color, (x, y, button_width, button_height))
        for evnt in pygame.event.get():
            if evnt.type == pygame.MOUSEBUTTONUP:
                if click_sound:
                    print("No default click sound has been set")
                return True
    else:
        pygame.draw.rect(Screen.screen, default_color, (x, y, button_width, button_height))

    Screen.screen.blit(button_msg, (x + button_width / 10, y + button_height / 10))
