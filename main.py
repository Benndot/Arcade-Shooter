import pygame
import sys
from game_utils import Font, create_title_text, create_text_button

pygame.init()

pygame.display.set_caption("Benndot's Space Invaders")

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


class Entity:

    def __init__(self, name: str, form: Image, x: float or int, y: float or int):
        self.name = name
        self.form = form
        self.x = x
        self.y = y

    def display(self):
        Screen.screen.blit(self.form.image, (self.x, self.y))


class Battler(Entity):

    def __init__(self, name, form, x, y, health):
        super().__init__(name, form, x, y)
        self.health = health
        self.momentum = 0


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

    player_image = Image("images/dad.png", Screen.game_zone / 11, Screen.game_zone / 11)
    player = Battler("Player", player_image, Screen.width / 2, Screen.height - player_image.height, 3)

    while True:

        backdrop.display_center()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evnt.type == pygame.KEYDOWN:
                if evnt.key == pygame.K_RIGHT:
                    player.momentum = Screen.height / 112
                if evnt.key == pygame.K_LEFT:
                    player.momentum = - Screen.height / 112
            if evnt.type == pygame.KEYUP:
                if evnt.key == pygame.K_RIGHT or evnt.key == pygame.K_LEFT:
                    player.momentum = 0
                if evnt.key == pygame.K_ESCAPE:
                    main()

        if player.momentum != 0:
            player.x += player.momentum
            if player.x <= (Screen.width - backdrop.image.get_width()) / 2:
                player.x = (Screen.width - backdrop.image.get_width()) / 2
            if player.x >= ((Screen.width - backdrop.image.get_width()) / 2) + backdrop.width - player.form.width:
                player.x = ((Screen.width - backdrop.image.get_width()) / 2) + backdrop.width - player.form.width

        player.display()

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
