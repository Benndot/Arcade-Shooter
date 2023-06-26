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


class Display:
    dimensions_540p_resolution = (960, 540)
    dimensions_720p_resolution = (1280, 720)
    dimensions_900p_resolution = (1600, 900)
    dimensions_1080p_resolution = (1920, 1080)
    screen_ratio: float = 0.5625
    width = 1600
    height = 900
    screen = pygame.display.set_mode((width, height))
    game_zone = width * 0.66

    @staticmethod
    def update_screen_and_game_zone():
        Display.screen = pygame.display.set_mode((Display.width, Display.height))
        Display.game_zone = Display.width * 0.66

    @staticmethod
    def set_resolution(dimensions: tuple[int, int]):
        width, height = dimensions[0], dimensions[1]
        Display.width = width
        Display.height = height
        Display.update_screen_and_game_zone()


class Font:

    def __init__(self, font_name: str, size_factor: float):
        self.font_name = font_name
        self.size_factor = size_factor
        self.font = pygame.font.SysFont(self.font_name, math.ceil(Display.height * 0.0695 * self.size_factor))

    def update(self):
        self.font = pygame.font.SysFont(self.font_name, math.ceil(Display.height * 0.0695 * self.size_factor))


class Fonts:
    xxl = Font("bahnschrift", 1.4)
    xl = Font("bahnschrift", 1.2)
    lg = Font("bahnschrift", 1)
    med_lg = Font("bahnschrift", 0.8)
    med = Font("bahnschrift", 0.6)
    sml_med = Font("bahnschrift", 0.45)
    sml = Font("bahnschrift", 0.33)

    font_list = [sml, sml_med, med, med_lg, lg, xl, xxl]

    @staticmethod
    def update_fonts():
        for font in Fonts.font_list:
            font.update()

# Utility functions for text and buttons ----------------------------------------------------------------------------


def create_onscreen_text(font_size, color, message, x, y, x_adjust: bool = False, screen=Display.screen):

    text = font_size.render(message, True, color)

    if x_adjust:
        text_width = text.get_width()
        x = x - (text_width / 2)

    screen.blit(text, (x, y))


def create_title_text(message, font_size=Fonts.lg.font, color=(0, 0, 0), x=Display.width / 2, y=Display.height * 0.1,
                      screen=Display.screen):

    render_text = font_size.render(message, True, color)
    adjusted_x = x - (render_text.get_width() / 2)
    screen.blit(render_text, (adjusted_x, y))


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


def create_transparent_button(width, height, x, y, screen=Display.screen):

    mouse = pygame.mouse.get_pos()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        s = pygame.Surface((width, height))  # the size of your rect
        s.set_alpha(128)  # alpha level
        s.fill((255, 255, 255))  # this fills the entire surface
        screen.blit(s, (x, y))  # (0,0) are the top-left coordinates
        for evnt in pygame.event.get():
            if evnt.type == pygame.MOUSEBUTTONUP:
                return True


def create_text_button(font_choice, msg: str, x: int or float, y: int or float,
                       text_color: tuple[int, int, int] = Color.black,
                       default_color: tuple[int, int, int] = Color.slategray,
                       hover_color: tuple[int, int, int] = Color.lightgray,
                       x_adjust: bool = False, click_sound: bool = True, screen=Display.screen):

    mouse = pygame.mouse.get_pos()

    button_msg = font_choice.render(msg, True, text_color)

    button_width = button_msg.get_width() + (button_msg.get_width() * 0.20)
    button_height = button_msg.get_height() + (button_msg.get_height() * 0.20)

    if x_adjust:
        x = x - (button_width / 2)

    # The experimental version
    if x + button_width > mouse[0] > x and y + button_height > mouse[1] > y:
        pygame.draw.rect(screen, hover_color, (x, y, button_width, button_height))
        for evnt in pygame.event.get():
            if evnt.type == pygame.MOUSEBUTTONUP:
                try:
                    if click_sound:
                        click = mixer.Sound("audio/click3.wav")
                        mixer.Sound.play(click)
                except FileNotFoundError:
                    print("There is no valid audio file for the clicking sound effect, at present")
                return True
    else:
        pygame.draw.rect(screen, default_color, (x, y, button_width, button_height))

    screen.blit(button_msg, (x + button_width / 10, y + button_height / 10))
