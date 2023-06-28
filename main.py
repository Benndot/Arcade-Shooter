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
    def __init__(self, image_path: str, scale: int, custom_width: callable = None, custom_height: callable = None):
        self.image_path = image_path
        self.scale = scale
        self.custom_width = custom_width  # Optional function input to change the dimensions
        self.custom_height = custom_height
        self.raw_image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

    @property
    def width(self):
        return Display.game_zone / self.scale if not self.custom_width else self.custom_width()

    @property
    def height(self):
        return Display.game_zone / self.scale if not self.custom_height else self.custom_height()

    @property
    def image(self):
        return pygame.transform.scale(self.raw_image, (self.width, self.height))

    def display_self(self, x, y):
        Display.screen.blit(self.image, (x, y))

    def center_on_screen(self):
        adjusted_x = (Display.width - self.image.get_width()) / 2
        Display.screen.blit(self.image, (adjusted_x, 0))

    def update_size_and_rect(self):
        self.rect = self.image.get_rect()


class Images:

    default_enemy_scale = 11

    player = Image("images/dad.png", 11)
    backdrop = Image("images/backdrop_park.png", 1, custom_height=Display.screen.get_height)
    hippy_speed = Image("images/hippie_brown.png", 11)
    hippy_basic = Image("images/hippie_green.png", 11)
    hippy_greater = Image("images/hippie_red.png", 11)
    projectile = Image("images/baseball.png", 25)

    images_list = [player, backdrop, hippy_speed, hippy_basic, hippy_greater, projectile]

    @staticmethod
    def update_all_images():
        for image in Images.images_list:
            image.update_size_and_rect()


class Entity:

    def __init__(self, form: Image, x: float or int, y: float or int, speed_divisor: int):
        self.form = form
        self.x = x
        self.y = y
        self.speed_divisor = speed_divisor
        self.rect = pygame.Rect(self.x, self.y, self.form.image.get_rect().width, self.form.image.get_rect().height)

    def display(self):
        Display.screen.blit(self.form.image, (self.x, self.y))

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.form.image.get_rect().width, self.form.image.get_rect().height)


class Projectile(Entity):

    def __init__(self, form, x, y, speed_divisor):
        super().__init__(form, x, y, speed_divisor)

    @property
    def speed(self):
        return Display.height / self.speed_divisor


class Enemy(Entity):

    def __init__(self, name: str, form: Image, health: int, speed_divisor: int, descent: float, x=0, y=0):
        super().__init__(form, x, y, speed_divisor)
        self.name = name
        self.health = health
        self.descent = descent
        self.has_projectiles = False
        self.invulnerable = False
        self.reverse_motion = random.choice([True, False])

    @property
    def speed(self):
        if self.reverse_motion:
            return - Display.height / self.speed_divisor
        else:
            return Display.height / self.speed_divisor

    def __str__(self):
        return f"{self.name}, x: {self.x}, y: {self.y}"


hippy_speed = Enemy("Speed Hippy", Images.hippy_speed, 1, 90, Display.height / 30)
hippy_basic = Enemy("Lesser Hippy", Images.hippy_basic, 2, 150, Display.height / 40)
hippy_greater = Enemy("Greater Hippy", Images.hippy_greater, 3, 120, Display.height / 50)


class Player(Entity):

    def __init__(self, form, health, speed=0, speed_divisor=112, x=0, y=0):
        super().__init__(form, x, y, speed_divisor)
        self.health = health
        self.speed = speed
        self.projectiles = []
        self.max_projectiles = 3

    def place_initial_position(self):
        self.y = Display.screen.get_height() - self.form.height
        self.x = (Display.screen.get_width() - self.form.width) / 2

    def controls(self, evnt):
        if evnt.type == pygame.KEYDOWN:
            if evnt.key == pygame.K_RIGHT or evnt.key == pygame.K_d:
                self.speed = Display.height / self.speed_divisor
            if evnt.key == pygame.K_LEFT or evnt.key == pygame.K_a:
                self.speed = - Display.height / self.speed_divisor
            if evnt.key == pygame.K_SPACE:
                self.launch_projectile()
        if evnt.type == pygame.KEYUP:
            if evnt.key == pygame.K_RIGHT or evnt.key == pygame.K_LEFT or evnt.key == pygame.K_d or \
                    evnt.key == pygame.K_a:
                self.speed = 0

    def move(self):
        if self.speed != 0:
            self.x += self.speed
            if self.x <= (Display.width - Display.game_zone) / 2:
                self.x = (Display.width - Display.game_zone) / 2
            if self.x >= ((Display.width - Display.game_zone) / 2) + Display.game_zone - self.form.width:
                self.x = ((Display.width - Display.game_zone) / 2) + Display.game_zone - self.form.width
        self.update_rect()
        self.display()

    def launch_projectile(self):
        if len(self.projectiles) < self.max_projectiles:
            projectile = Projectile(Images.projectile, self.x + (Images.projectile.width / 2),
                                    self.y - Display.height / 30, 112)
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
        # self.height = Display.height
        self.left_boundary = (Display.width - background.width) / 2
        self.right_boundary = ((Display.width - background.width) / 2) + background.width
        self.margin_width = (Display.width - background.width) / 2

    def get_entity_right_boundary(self, entity):
        return self.right_boundary - entity.form.width

    def update_boundaries(self):
        self.left_boundary = (Display.width - self.background.width) / 2
        self.right_boundary = ((Display.width - self.background.width) / 2) + self.background.width


class Arenas:
    park = Arena(Images.backdrop)


class Stage(Arena):

    def __init__(self, stage_id: int, name: str, background: Image, enemy_details: tuple, song: Song):
        super().__init__(background)
        self.stage_id = stage_id
        self.name = name
        self.enemy_details = enemy_details
        self.enemy_list: list[Enemy] = []
        self.player = Player(Images.player, 3, x=Display.width / 2, y=Display.height - Images.player.height)
        self.song = song
        self.is_complete: bool = False

    def generate_enemy_positions(self):
        for entry in self.enemy_details:
            for _ in range(entry["count"]):
                enemy = copy.copy(entry["enemy"])

                x = random.randint(int(self.left_boundary), int(self.get_entity_right_boundary(enemy)))
                enemy.x = x

                y = random.randint(0, int(Display.height * 0.5))
                enemy.y = y

                self.enemy_list.append(enemy)

    def move_enemies(self):
        for enemy in self.enemy_list:
            enemy.x += enemy.speed
            if enemy.x <= self.left_boundary or enemy.x >= self.get_entity_right_boundary(enemy):
                enemy.y += enemy.descent
                enemy.reverse_motion = not enemy.reverse_motion
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
                      {"enemy": hippy_basic, "count": 6},

                      {"enemy": hippy_greater, "count": 3}
                  ),
                  Sound.song_winters_love
                  )

stage_two = Stage(2, "Camp", Images.backdrop,
                  (
                      {"enemy": hippy_basic, "count": 4},

                      {"enemy": hippy_greater, "count": 3},

                      {"enemy": hippy_speed, "count": 4}
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
    Fonts.update_fonts()

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
                Images.update_all_images()
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

    stage.song.play()

    stage.update_boundaries()

    stage.generate_enemy_positions()

    background: Image = Game.current_stage.background

    stage.player.place_initial_position()

    while True:

        Display.screen.fill((0, 0, 0))

        background.center_on_screen()

        create_title_text(f"Stage 1", color=(200, 200, 200), x=stage.margin_width / 2, y=Display.height*0.02,
                          screen=Display.screen)
        create_title_text(f"{stage.name}", color=(255, 255, 255), x=stage.margin_width / 2, y=Display.height*0.1,
                          screen=Display.screen)

        for evnt in pygame.event.get():
            Game.quit(evnt)
            stage.player.controls(evnt)
            if evnt.type == pygame.KEYUP:
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
