import pygame
import sys
import copy
import random
from game_utils import Font, create_title_text, create_text_button

pygame.init()

pygame.display.set_caption("Benndot's Space Invaders")

clock = pygame.time.Clock()


class Display:
    width = 1600
    height = 900
    screen = pygame.display.set_mode((width, height))
    game_zone = width * 0.66


class Image:
    def __init__(self, image_path: str, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.raw_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.raw_image, (width, height))

    def display_self(self, x, y):
        Display.screen.blit(self.image, (x, y))

    def display_center(self):
        adjusted_x = (Display.width - self.image.get_width()) / 2
        Display.screen.blit(self.image, (adjusted_x, 0))


class Images:
    player_image = Image("images/dad.png", Display.game_zone / 11, Display.game_zone / 11)
    backdrop = Image("images/backdrop_park.png", Display.width * 0.66, Display.height)
    lesser_hippy = Image("images/hippie_green.png", Display.game_zone / 11, Display.game_zone / 11)
    greater_hippy = Image("images/hippie_red.png", Display.game_zone / 11, Display.game_zone / 11)


class Entity:

    def __init__(self, form: Image, x: float or int, y: float or int):
        self.form = form
        self.x = x
        self.y = y

    def display(self):
        Display.screen.blit(self.form.image, (self.x, self.y))


class Enemy(Entity):

    def __init__(self, name: str, form: Image, health: int, x=None, y=None):
        super().__init__(form, x, y)
        self.name = name
        self.health = health
        self.speed = Display.height / 112

    def __str__(self):
        return f"{self.name}, x: {self.x}, y: {self.y}"


lesser_hippy = Enemy("Lesser Hippy", Images.lesser_hippy, 1)
greater_hippy = Enemy("Greater Hippy", Images.greater_hippy, 2)


class Player(Entity):

    def __init__(self, form, x, y, health):
        super().__init__(form, x, y)
        self.health = health
        self.momentum = 0
        self.projectile_image = Image("images/baseball.png", Display.game_zone / 20, Display.game_zone / 20)
        self.projectiles = []

    def move(self):
        if self.momentum != 0:
            self.x += self.momentum
            if self.x <= (Display.width - Display.game_zone) / 2:
                self.x = (Display.width - Display.game_zone) / 2
            if self.x >= ((Display.width - Display.game_zone) / 2) + Display.game_zone - self.form.width:
                self.x = ((Display.width - Display.game_zone) / 2) + Display.game_zone - self.form.width
        self.display()

    def move_projectiles(self):
        for projectile in self.projectiles:
            projectile.y -= Display.height / 112
            if projectile.y < -50:
                self.projectiles.remove(projectile)
            projectile.display()


class Stage:

    def __init__(self, background, enemy_details):
        self.background: Image = background
        self.enemy_details: tuple[dict] = enemy_details
        self.enemy_list: list = []

    def generate_enemy_positions(self):
        for entry in self.enemy_details:
            for _ in range(entry["count"]):
                enemy = copy.copy(entry["enemy"])
                print("hello")
                if len(entry["x"]) == 2:
                    position = random.randint(entry["x"][0], entry["x"][1])
                    print(f"X: {position}")
                    enemy.x = position
                else:
                    enemy.x = entry["x"][0]

                if len(entry["y"]) == 2:
                    position = random.randint(entry["y"][0], entry["y"][1])
                    print(f"Y: {position}")
                    enemy.y = position
                else:
                    enemy.y = entry["y"][0]

                self.enemy_list.append(enemy)


stage_one = Stage(Images.backdrop,
                  (
                      {"enemy": lesser_hippy, "count": 5, "x": [(Display.width - Images.backdrop.width) / 2,
                                                                (Display.width - Images.backdrop.width) / 2 +
                                                                Images.backdrop.width - lesser_hippy.form.width],
                       "y": [0, Display.height / 2.25]},
                      {"enemy": greater_hippy, "count": 2, "x": [(Display.width - Images.backdrop.width) / 2,
                                                                 (Display.width - Images.backdrop.width) / 2 +
                                                                 Images.backdrop.width - greater_hippy.form.width],
                       "y": [0, Display.height / 2.25]}
                  )
                  )


class Game:
    fps: int = 60
    current_stage: Stage = stage_one


# GAME SCREENS --------------------------------------------------------------------------------------------------------


def start_menu():

    while True:
        Display.screen.fill((0, 0, 0))

        create_title_text("Benndot's Arcade Shooter", color=(255, 255, 255), x=Display.width * 0.5,
                          screen=Display.screen)

        play_button = create_text_button(Font.lg, "PLAY", Display.width * 0.5, Display.height * 0.5,
                                         x_adjust=True, screen=Display.screen)

        if play_button:
            game()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(Game.fps)


def game():

    background: Image = Game.current_stage.background

    stage_one.generate_enemy_positions()
    for enemy in stage_one.enemy_list:
        print(enemy.__str__())

    Display.screen.fill((0, 0, 0))

    player = Player(Images.player_image, Display.width / 2, Display.height - Images.player_image.height, 3)

    while True:

        background.display_center()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evnt.type == pygame.KEYDOWN:
                if evnt.key == pygame.K_RIGHT or evnt.key == pygame.K_d:
                    player.momentum = Display.height / 112
                if evnt.key == pygame.K_LEFT or evnt.key == pygame.K_a:
                    player.momentum = - Display.height / 112
                if evnt.key == pygame.K_SPACE:
                    projectile = Entity(player.projectile_image, player.x + (player.projectile_image.width / 2),
                                        player.y - Display.height / 30)
                    player.projectiles.append(projectile)
            if evnt.type == pygame.KEYUP:
                if evnt.key == pygame.K_RIGHT or evnt.key == pygame.K_LEFT or evnt.key == pygame.K_d or \
                        evnt.key == pygame.K_a:
                    player.momentum = 0
                if evnt.key == pygame.K_ESCAPE:
                    main()

        player.move()

        player.move_projectiles()

        for enemy in stage_one.enemy_list:
            enemy.display()

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
