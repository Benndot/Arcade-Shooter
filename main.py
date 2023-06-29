import pygame
from pygame import mixer
import sys
import copy
import random
from game_utils import Fonts, Display, create_onscreen_text, create_title_text, create_text_button

pygame.init()

pygame.display.set_caption("Benndot's Space Invaders")

clock = pygame.time.Clock()


class Song:

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path


class Sound:
    song_afterthought = Song("Afterthought", "audio/music-afterthought.mp3")
    song_winters_love1 = Song("Winter's Love (Part 1)", "audio/music-winters_love_part1.mp3")
    song_winters_love2 = Song("Winter's Love (Part 2)", "audio/music-winters_love_part2.mp3")
    victory = Song("The Debt Collector", "audio/music-debt_collector.mp3")
    defeat = Song("Coffee and TV outro", "audio/music-coffee_and_tv_outro.mp3")
    soundtrack: list[Song] = [song_afterthought, song_winters_love1, song_winters_love2]

    def __init__(self):
        self.music_playing = False
        self.current_track = None
        self.current_track_paused = None

    def play_track(self, loop=True, fade_ms=None):
        self.music_playing = True
        mixer.music.play(-1 if loop else 0, fade_ms=fade_ms if fade_ms else 0)

    def stop_track(self):
        self.music_playing = False
        mixer.music.stop()
        mixer.music.unload()

    def set_and_play_track(self, song, loop=True, fade_ms=None):
        self.current_track = song
        mixer.music.load(self.current_track.path)
        self.play_track(loop=loop, fade_ms=fade_ms)

    def toggle_track(self):
        if self.current_track:
            self.current_track_paused = not self.current_track_paused
            if self.current_track_paused:
                self.music_playing = True
                mixer.music.unpause()
            else:
                self.music_playing = False
                mixer.music.pause()


sound = Sound()


class Image:
    def __init__(self, image_path: str, scale: int, custom_width: callable = None, custom_height: callable = None):
        self.image_path = image_path
        self.scale = scale
        self.custom_width = custom_width  # Optional function input to change the dimensions
        self.custom_height = custom_height
        self.raw_image = pygame.image.load(image_path)

    @property
    def width(self):
        return Display.game_zone / self.scale if not self.custom_width else self.custom_width()

    @property
    def height(self):
        return Display.game_zone / self.scale if not self.custom_height else self.custom_height()

    @property
    def image(self):
        return pygame.transform.scale(self.raw_image, (self.width, self.height))

    @property
    def rect(self):
        return self.image.get_rect()

    def display_self(self, x, y):
        Display.screen.blit(self.image, (x, y))

    def center_on_screen(self):
        adjusted_x = (Display.width - self.image.get_width()) / 2
        Display.screen.blit(self.image, (adjusted_x, 0))


class Images:

    default_enemy_scale = 11

    player = Image("images/dad.png", 11)
    backdrop = Image("images/backdrop_park.png", 1, custom_height=Display.screen.get_height)
    camp = Image("images/camp.jpg", 1, custom_height=Display.screen.get_height)
    victory = Image("images/victory_screen.jpg", 1, custom_height=Display.screen.get_height)
    defeat = Image("images/defeat_screen.jpg", 1, custom_height=Display.screen.get_height)
    hippy_speed = Image("images/hippie_brown.png", 11)
    hippy_basic = Image("images/hippie_green.png", 11)
    hippy_greater = Image("images/hippie_red.png", 11)
    projectile = Image("images/baseball.png", 25)

    images_list = [player, backdrop, hippy_speed, hippy_basic, hippy_greater, projectile]


class Entity:

    def __init__(self, form: Image, x: float or int, y: float or int, speed_divisor: int):
        self.form = form
        self.x = x
        self.y = y
        self.speed_divisor = speed_divisor
        self.rect = pygame.Rect(self.x, self.y, self.form.image.get_rect().width, self.form.image.get_rect().height)

    def display_entity(self):
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

    def __init__(self, form, speed=0, speed_divisor=112, x=0, y=0):
        super().__init__(form, x, y, speed_divisor)
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
        self.display_entity()

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
            projectile.display_entity()


class Arena:

    def __init__(self, background: Image):
        self.background: Image = background
        # self.height = Display.height

    @property
    def left_boundary(self):
        return (Display.width - self.background.width) / 2

    @property
    def right_boundary(self):
        return ((Display.width - self.background.width) / 2) + self.background.width

    @property
    def margin_width(self):
        return (Display.width - self.background.width) / 2

    @property
    def right_margin_x(self):
        return Display.width - self.margin_width

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
        self.song = song
        self.enemy_list: list[Enemy] = []
        self.player = Player(Images.player, x=Display.width / 2, y=Display.height - Images.player.height)
        self.is_complete: bool = False
        self.is_cleared: bool = False

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
            enemy.display_entity()

    def detect_collision(self):
        for projectile in self.player.projectiles:
            for enemy in self.enemy_list:
                if not enemy.invulnerable and projectile.rect.colliderect(enemy):
                    thump = mixer.Sound("audio/thump.mp3")
                    mixer.Sound.play(thump)
                    try:
                        self.player.projectiles.remove(projectile)
                    except ValueError:
                        pass
                    enemy.health -= 1
                    if enemy.health <= 0:
                        self.enemy_list.remove(enemy)
                        ow = mixer.Sound("audio/ow.mp3")
                        mixer.Sound.play(ow)
                    enemy.invulnerable = True
                if enemy.invulnerable and not projectile.rect.colliderect(enemy):
                    enemy.invulnerable = False

    def user_interface(self):
        create_title_text(f"Stage {self.stage_id}", color=(200, 200, 200), x=self.margin_width / 2,
                          y=Display.height * 0.02, screen=Display.screen)
        create_title_text(f"{self.name}", color=(255, 255, 255), x=self.margin_width / 2, y=Display.height * 0.1,
                          screen=Display.screen)

        create_onscreen_text(Fonts.med.font, (200, 200, 200), f"Remaining", self.right_margin_x +
                             self.margin_width / 2, Display.height * 0.02, True, Display.screen)
        create_title_text(f"{len(self.enemy_list)}", color=(255, 255, 255),
                          x=self.right_margin_x + self.margin_width / 2, y=Display.height * 0.08,
                          screen=Display.screen)


stage_one = Stage(1, "Park", Images.backdrop,
                  (
                      {"enemy": hippy_basic, "count": 6},

                      {"enemy": hippy_greater, "count": 3}
                  ),
                  Sound.song_winters_love1
                  )

stage_two = Stage(2, "Camp", Images.camp,
                  (
                      {"enemy": hippy_basic, "count": 4},

                      {"enemy": hippy_greater, "count": 3},

                      {"enemy": hippy_speed, "count": 4}
                  ),
                  Sound.song_winters_love2
                  )


class Game:
    fps: int = 60
    stage_list: list[Stage] = [stage_one, stage_two]
    current_stage: Stage = stage_two

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
                next_function()

            button_pos_offset += 0.15

        for evnt in pygame.event.get():
            Game.quit(evnt)

        pygame.display.update()
        clock.tick(Game.fps)


def start_menu():

    if sound.current_track != Sound.song_afterthought:
        sound.set_and_play_track(Sound.song_afterthought)

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

        back_button = create_text_button(Fonts.lg.font, "Back", Display.width * 0.5, Display.height * 0.65,
                                         x_adjust=True, screen=Display.screen)

        if back_button:
            start_menu()

        for event in pygame.event.get():
            Game.quit(event)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    main()

        pygame.display.update()
        clock.tick(Game.fps)


def game(stage: Stage):

    sound.set_and_play_track(stage.song)

    stage.generate_enemy_positions()

    background: Image = Game.current_stage.background

    stage.player.place_initial_position()

    while True:

        Display.screen.fill((0, 0, 0))

        background.center_on_screen()

        stage.user_interface()

        # Images.hippy_greater.display_self(stage.right_margin_x + Display.width / 100, Display.height * 0.5)

        for evnt in pygame.event.get():
            Game.quit(evnt)
            stage.player.controls(evnt)
            if evnt.type == pygame.KEYUP:
                if evnt.key == pygame.K_ESCAPE:
                    stage.player.projectiles = []
                    stage.enemy_list = []  # Only reset currently
                    mixer.music.fadeout(2000)
                    main()
                if evnt.key == pygame.K_m:
                    sound.toggle_track()

        Game.current_stage.move_enemies()

        stage.player.move()
        stage.player.move_projectiles()

        stage.detect_collision()

        # Early form of victory condition
        if not stage.enemy_list:
            stage.player.y = Display.height * -0.5
            background = Images.victory
            stage.is_complete = True
            stage.is_cleared = True
            if sound.current_track != Sound.victory:
                sound.set_and_play_track(Sound.victory, fade_ms=2000)
            create_title_text(f"STAGE {stage.stage_id} CLEARED", color=(255, 255, 255), x=Display.width / 2,
                              y=Display.height * 0.6, screen=Display.screen, font=Fonts.xl.font)

            continue_button = create_text_button(Fonts.lg.font, "Continue", Display.width * 0.5, Display.height * 0.75,
                                                 x_adjust=True, screen=Display.screen)

            if continue_button:
                start_menu()

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
