import pygame
from pygame import mixer
import sys
import copy
import random
from game_utils import Fonts, Display, create_title_text, create_text_button

pygame.init()

pygame.display.set_caption("Benndot's Space Invaders")

clock = pygame.time.Clock()


class Song:

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def play(self):
        mixer.music.load(self.path)
        mixer.music.play(-1)


class Sound:
    song_afterthought = Song("Afterthought", "audio/music-afterthought.mp3")
    song_winters_love = Song("Winter's Love", "audio/music-winters_love.mp3")
    soundtrack: list[Song] = [song_afterthought, song_winters_love]


class Image:
    def __init__(self, image_path: str, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.raw_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.raw_image, (width, height))
        self.rect = self.image.get_rect()

    def display_self(self, x, y):
        Display.screen.blit(self.image, (x, y))

    def display_center(self):
        adjusted_x = (Display.width - self.image.get_width()) / 2
        Display.screen.blit(self.image, (adjusted_x, 0))


class Images:

    default_enemy_size = Display.game_zone / 11, Display.game_zone / 11

    player = Image("images/dad.png", Display.game_zone / 11, Display.game_zone / 11)
    backdrop = Image("images/backdrop_park.png", Display.width * 0.66, Display.height)
    hippy_speed = Image("images/hippie_brown.png", default_enemy_size[0], default_enemy_size[1])
    hippy_basic = Image("images/hippie_green.png", default_enemy_size[0], default_enemy_size[1])
    hippy_greater = Image("images/hippie_red.png", default_enemy_size[0], default_enemy_size[1])
    projectile = Image("images/baseball.png", Display.game_zone / 25, Display.game_zone / 25)


class Entity:

    def __init__(self, form: Image, x: float or int, y: float or int):
        self.form = form
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.form.image.get_rect().width, self.form.image.get_rect().height)

    def display(self):
        Display.screen.blit(self.form.image, (self.x, self.y))

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.form.image.get_rect().width, self.form.image.get_rect().height)


class Projectile(Entity):

    def __init__(self, form, x, y, speed):
        super().__init__(form, x, y)
        self.speed = speed


class Enemy(Entity):

    def __init__(self, name: str, form: Image, health: int, speed, descent, x=0, y=0):
        super().__init__(form, x, y)
        self.name = name
        self.health = health
        self.speed = speed
        self.descent = descent
        self.has_projectiles = False
        self.invulnerable = False

    def __str__(self):
        return f"{self.name}, x: {self.x}, y: {self.y}"


hippy_speed = Enemy("Speed Hippy", Images.hippy_speed, 1, Display.height / 90, 21)
hippy_basic = Enemy("Lesser Hippy", Images.hippy_basic, 2, Display.height / 150, 14)
hippy_greater = Enemy("Greater Hippy", Images.hippy_greater, 3, Display.height / 120, 7)


class Player(Entity):

    def __init__(self, form, x, y, health):
        super().__init__(form, x, y)
        self.health = health
        self.momentum = 0
        self.projectiles = []
        self.max_projectiles = 3

    def move(self):
        if self.momentum != 0:
            self.x += self.momentum
            if self.x <= (Display.width - Display.game_zone) / 2:
                self.x = (Display.width - Display.game_zone) / 2
            if self.x >= ((Display.width - Display.game_zone) / 2) + Display.game_zone - self.form.width:
                self.x = ((Display.width - Display.game_zone) / 2) + Display.game_zone - self.form.width
        self.update_rect()
        self.display()

    def launch_projectile(self):
        if len(self.projectiles) < self.max_projectiles:
            projectile = Projectile(Images.projectile, self.x + (Images.projectile.width / 2),
                                    self.y - Display.height / 30, Display.height / 112)
            self.projectiles.append(projectile)

    def move_projectiles(self):
        for projectile in self.projectiles:
            projectile.y -= projectile.speed
            if projectile.y < -50:
                self.projectiles.remove(projectile)
            projectile.update_rect()
            projectile.display()


class Arena:

    def __init__(self, background: Image):
        self.background: Image = background
        self.height = Display.height
        self.left_boundary = (Display.width - background.width) / 2
        self.right_boundary = ((Display.width - background.width) / 2) + background.width
        self.margin_width = (Display.width - background.width) / 2

    def get_entity_right_boundary(self, entity):
        return self.right_boundary - entity.form.width


class Arenas:
    park = Arena(Images.backdrop)


class Stage(Arena):

    def __init__(self, stage_id: int, name: str, background: Image, enemy_details: tuple, song: Song):
        super().__init__(background)
        self.stage_id = stage_id
        self.name = name
        self.enemy_details = enemy_details
        self.enemy_list: list[Enemy] = []
        self.player = Player(Images.player, Display.width / 2, Display.height - Images.player.height, 3)
        self.song = song
        self.is_complete: bool = False

    def generate_enemy_positions(self):
        for entry in self.enemy_details:
            for _ in range(entry["count"]):
                enemy = copy.copy(entry["enemy"])
                if len(entry["x"]) == 2:
                    position = random.randint(int(entry["x"][0]), int(entry["x"][1]))
                    enemy.x = position
                else:
                    enemy.x = entry["x"][0]

                if len(entry["y"]) == 2:
                    position = random.randint(entry["y"][0], entry["y"][1])
                    enemy.y = position
                else:
                    enemy.y = entry["y"][0]

                enemy.speed = random.choice([enemy.speed, -enemy.speed])

                self.enemy_list.append(enemy)

    def move_enemies(self):
        for enemy in self.enemy_list:
            enemy.x += enemy.speed
            if enemy.x <= self.left_boundary or enemy.x >= self.get_entity_right_boundary(enemy):
                enemy.y += enemy.descent
                enemy.speed = -enemy.speed
            enemy.update_rect()
            enemy.display()

    def detect_collision(self):
        for projectile in self.player.projectiles:
            for enemy in stage_one.enemy_list:
                if not enemy.invulnerable and projectile.rect.colliderect(enemy):
                    thump = mixer.Sound("audio/thump.mp3")
                    mixer.Sound.play(thump)
                    try:
                        self.player.projectiles.remove(projectile)
                    except ValueError:
                        pass
                    enemy.health -= 1
                    if enemy.health <= 0:
                        stage_one.enemy_list.remove(enemy)
                        ow = mixer.Sound("audio/ow.mp3")
                        mixer.Sound.play(ow)
                    enemy.invulnerable = True
                if enemy.invulnerable and not projectile.rect.colliderect(enemy):
                    enemy.invulnerable = False


stage_one = Stage(1, "Park", Images.backdrop,
                  (
                      {"enemy": hippy_basic, "count": 6, "x": [Arenas.park.left_boundary,
                                                               Arenas.park.get_entity_right_boundary(hippy_basic)],
                       "y": [0, Display.height / 2.25]},

                      {"enemy": hippy_greater, "count": 3, "x": [Arenas.park.left_boundary,
                                                                 Arenas.park.get_entity_right_boundary(hippy_greater)],
                       "y": [0, Display.height / 2.25]}
                  ),
                  Sound.song_winters_love
                  )

stage_two = Stage(2, "Camp", Images.backdrop,
                  (
                      {"enemy": hippy_basic, "count": 4, "x": [Arenas.park.left_boundary,
                                                               Arenas.park.get_entity_right_boundary(hippy_basic)],
                       "y": [0, Display.height / 2.25]},

                      {"enemy": hippy_greater, "count": 3, "x": [Arenas.park.left_boundary,
                                                                 Arenas.park.get_entity_right_boundary(hippy_greater)],
                       "y": [0, Display.height / 2.25]},

                      {"enemy": hippy_speed, "count": 4, "x": [Arenas.park.left_boundary,
                                                               Arenas.park.get_entity_right_boundary(hippy_speed)],
                       "y": [0, Display.height / 2.25]}
                  ),
                  Sound.song_winters_love
                  )


class Game:
    fps: int = 60
    stage_list: list[Stage] = [stage_one, stage_two]
    current_stage: Stage = stage_one

    @staticmethod
    def quit(event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

# GAME SCREENS --------------------------------------------------------------------------------------------------------


def choose_resolution(next_function: callable):
    Display.set_resolution(Display.dimensions_540p_resolution)

    resolutions: list[tuple[int, int]] = [Display.dimensions_540p_resolution, Display.dimensions_720p_resolution,
                                          Display.dimensions_900p_resolution, Display.dimensions_1080p_resolution]
    resolution_names: list[str] = ["540p", "720p", "900p", "1080p"]

    while True:
        Display.screen.fill((0, 0, 0))

        create_title_text("Choose Resolution", color=(255, 255, 255), x=Display.width * 0.5,
                          screen=Display.screen)

        button_pos_offset: float = 0.35

        for index, res in enumerate(resolutions):

            res_button = create_text_button(Fonts.lg.font, f"{resolution_names[index]}", Display.width * 0.5,
                                            Display.height * button_pos_offset, x_adjust=True, screen=Display.screen)

            if res_button:
                Display.set_resolution(res)
                Fonts.update_fonts()
                next_function()

            button_pos_offset += 0.15

        for evnt in pygame.event.get():
            Game.quit(evnt)

        pygame.display.update()
        clock.tick(Game.fps)


def start_menu():

    Sound.song_afterthought.play()

    while True:
        Display.screen.fill((0, 0, 0))

        create_title_text("Benndot's Arcade Shooter", color=(255, 255, 255), x=Display.width * 0.5,
                          screen=Display.screen)

        play_button = create_text_button(Fonts.xl.font, "PLAY", Display.width * 0.5, Display.height * 0.4,
                                         x_adjust=True, screen=Display.screen)

        if play_button:
            game(Game.current_stage)

        settings_button = create_text_button(Fonts.lg.font, "SETTINGS", Display.width * 0.5, Display.height * 0.65,
                                             x_adjust=True, screen=Display.screen)

        if settings_button:
            options()

        for evnt in pygame.event.get():
            Game.quit(evnt)

        pygame.display.update()
        clock.tick(Game.fps)


def options():

    while True:
        Display.screen.fill((255, 255, 255))

        create_title_text("Settings", color=(0, 0, 0), x=Display.width * 0.5,
                          screen=Display.screen)

        for event in pygame.event.get():
            Game.quit(event)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    main()

        pygame.display.update()
        clock.tick(Game.fps)


def game(stage: Stage):

    # Images.backdrop.update_size()
    #
    # for stage in Game.stage_list:
    #     stage.update_boundaries()
    #
    # print(f"Display dimensions: {Display.width} / {Display.height} / {Display.game_zone}")
    # print(Images.backdrop.width, Images.backdrop.height)
    # print(Game.current_stage.background.width, Game.current_stage.background.height)

    stage.song.play()

    background: Image = Game.current_stage.background

    stage_one.generate_enemy_positions()
    # for enemy in stage_one.enemy_list:
    #     print(enemy.__str__())

    Display.screen.fill((0, 0, 0))

    while True:

        background.display_center()

        create_title_text(f"Stage 1", color=(200, 200, 200), x=stage.margin_width / 2, y=Display.height*0.02,
                          screen=Display.screen)
        create_title_text(f"{stage.name}", color=(255, 255, 255), x=stage.margin_width / 2, y=Display.height*0.1,
                          screen=Display.screen)

        for evnt in pygame.event.get():
            Game.quit(evnt)
            if evnt.type == pygame.KEYDOWN:
                if evnt.key == pygame.K_RIGHT or evnt.key == pygame.K_d:
                    stage.player.momentum = Display.height / 112
                if evnt.key == pygame.K_LEFT or evnt.key == pygame.K_a:
                    stage.player.momentum = - Display.height / 112
                if evnt.key == pygame.K_SPACE:
                    stage.player.launch_projectile()
            if evnt.type == pygame.KEYUP:
                if evnt.key == pygame.K_RIGHT or evnt.key == pygame.K_LEFT or evnt.key == pygame.K_d or \
                        evnt.key == pygame.K_a:
                    stage.player.momentum = 0
                if evnt.key == pygame.K_ESCAPE:
                    stage.enemy_list = []  # Only reset currently
                    main()

        Game.current_stage.move_enemies()

        stage.player.move()
        stage.player.move_projectiles()

        stage.detect_collision()

        pygame.display.update()
        clock.tick(Game.fps)


def main():

    while True:

        choose_resolution(start_menu)

        for evnt in pygame.event.get():
            Game.quit(evnt)

        pygame.display.update()
        clock.tick(Game.fps)


if __name__ == "__main__":
    main()
