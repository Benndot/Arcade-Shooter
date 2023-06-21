import pygame
import sys
from game_utils import Font, create_title_text, create_text_button

pygame.init()

clock = pygame.time.Clock()


class Screen:
    width = 1600
    height = 900
    screen = pygame.display.set_mode((width, height))
    game_zone = width * 0.66


class Game:
    fps = 60


class Image:
    def __init__(self, image_path: str, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.raw_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.raw_image, (width, height))

    def display_self(self, x, y):
        Screen.screen.blit(self.image, (x, y))

    def display_center(self):
        adjusted_x = (Screen.width - self.image.get_width()) / 2
        Screen.screen.blit(self.image, (adjusted_x, 0))


def start_menu():

    while True:
        Screen.screen.fill((0, 0, 0))

        create_title_text("Benndot's Arcade Shooter", color=(255, 255, 255))

        play_button = create_text_button(Font.lg, "PLAY", Screen.width * 0.5, Screen.height * 0.5)

        if play_button:
            game()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(Game.fps)


def game():

    Screen.screen.fill((0, 0, 0))

    backdrop = Image("images/backdrop_park.png", Screen.width * 0.66, Screen.height)

    while True:

        backdrop.display_center()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evnt.type == pygame.KEYUP:
                if evnt.key == pygame.K_ESCAPE:
                    main()

        pygame.display.update()
        clock.tick(Game.fps)


def main():

    while True:

        start_menu()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(Game.fps)


if __name__ == "__main__":
    main()
