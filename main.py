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

    thump = mixer.Sound("audio/thump.mp3")
    ow = mixer.Sound("audio/ow.mp3")
    click = mixer.Sound("audio/click.wav")
    sound_effects = [thump, ow, click]

    def __init__(self):
        self.music_volume: float = 5
        self.sf_volume: float = 2
        self.music_playing: bool = False
        self.current_track: Song or None = None
        self.current_track_paused: bool = False

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

    def set_sf_volume(self):
        for sf in Sound.sound_effects:
            sf.set_volume(self.sf_volume / 10)

    def change_sf_volume(self, change: int):
        self.sf_volume += change
        if self.sf_volume > 10:
            self.sf_volume = 10
        elif self.sf_volume < 0:
            self.sf_volume = 0
        self.set_sf_volume()


sound = Sound()
sound.set_sf_volume()


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
    tent = Image("images/hippy_tent.jpg", 1, custom_height=Display.screen.get_height)
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

    def randomize_move_direction(self):
        self.reverse_motion = random.choice([True, False])

    def __str__(self):
        return f"{self.name}, x: {self.x}, y: {self.y}"


hippy_speed = Enemy("Speed Hippy", Images.hippy_speed, 2, 120, Display.height / 30)
hippy_basic = Enemy("Lesser Hippy", Images.hippy_basic, 3, 180, Display.height / 40)
hippy_greater = Enemy("Greater Hippy", Images.hippy_greater, 4, 150, Display.height / 50)


class Player(Entity):

    def __init__(self, form, speed=0, speed_divisor=112, x=0, y=0):
        super().__init__(form, x, y, speed_divisor)
        self.speed = speed
        self.projectiles = []
        self.max_projectiles = 2
        self.is_defeated: bool = False

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

    def reset(self):
        self.is_complete: bool = False
        self.player.projectiles = []
        self.enemy_list = []
        self.player.is_defeated = False
        mixer.music.fadeout(2000)

    def generate_enemy_positions(self):
        for entry in self.enemy_details:
            for _ in range(entry["count"]):
                enemy = copy.copy(entry["enemy"])

                x = random.randint(int(self.left_boundary), int(self.get_entity_right_boundary(enemy)))
                enemy.x = x

                y = random.randint(0, int(Display.height * 0.5))
                enemy.y = y

                enemy.randomize_move_direction()

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
                    mixer.Sound.play(Sound.thump)
                    try:
                        self.player.projectiles.remove(projectile)
                    except ValueError:
                        pass
                    enemy.health -= 1
                    if enemy.health <= 0:
                        self.enemy_list.remove(enemy)
                        mixer.Sound.play(Sound.ow)
                    enemy.invulnerable = True
                if enemy.invulnerable and not projectile.rect.colliderect(enemy):
                    enemy.invulnerable = False

        for enemy in self.enemy_list:
            if self.player.rect.colliderect(enemy):
                self.player.y = Display.height * -1
                self.player.is_defeated = True

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

    def post_game_screen(self, message: str, song: Song, image: Image):
        self.player.y = Display.height * -1
        Game.active_background = image
        if sound.current_track != song:
            sound.set_and_play_track(song, fade_ms=2000)

        create_title_text(message, color=(255, 255, 255), x=Display.width / 2,
                          y=Display.height * 0.6, screen=Display.screen, font=Fonts.xl)

        continue_button = create_text_button(Fonts.lg.font, "Continue", Display.width * 0.5, Display.height * 0.75,
                                             x_adjust=True, screen=Display.screen)

        if continue_button:
            self.reset()
            start_menu()


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

stage_three = Stage(3, "Boss", Images.tent,
                    (
                        {"enemy": hippy_basic, "count": 3},

                        {"enemy": hippy_greater, "count": 3},

                        {"enemy": hippy_speed, "count": 12}
                    ),
                    Sound.song_winters_love2
                    )


class Game:
    fps: int = 60
    stage_list: list[Stage] = [stage_one, stage_two, stage_three]
    current_stage: Stage = stage_two
    active_background: Image = None

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

        play_button = create_text_button(Fonts.xl.font, "PLAY", Display.width * 0.5, Display.height * 0.25,
                                         x_adjust=True, screen=Display.screen)

        if play_button:
            game(Game.current_stage)

        settings_button = create_text_button(Fonts.med_lg.font, "SETTINGS", Display.width * 0.5, Display.height * 0.45,
                                             x_adjust=True, screen=Display.screen)

        if settings_button:
            options()

        create_title_text(f"Selected Stage: {Game.current_stage.name}", color=(255, 255, 255), x=Display.width * 0.5,
                          screen=Display.screen, y=Display.height * 0.6, font=Fonts.med)

        mouse = pygame.mouse.get_pos()
        stage_icon_offset = 0
        for stage in Game.stage_list:
            icon = pygame.transform.scale(stage.background.raw_image, (Display.width / 9, Display.width / 16))
            x = Display.width * (0.25 + stage_icon_offset)
            y = Display.height * 0.75
            Display.screen.blit(icon, (x, y))

            if x + icon.get_width() > mouse[0] > x and y + icon.get_height() > mouse[1] > y:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        try:
                            mixer.Sound.play(Sound.click)
                        except FileNotFoundError:
                            pass
                        Game.current_stage = stage

            stage_icon_offset += 0.2

        for evnt in pygame.event.get():
            Game.quit(evnt)

        pygame.display.update()
        clock.tick(Game.fps)


def options():
    while True:
        Display.screen.fill((220, 220, 220))

        create_title_text("Settings", color=(0, 0, 0), x=Display.width * 0.5,
                          screen=Display.screen)

        res_button = create_text_button(Fonts.lg.font, "Change Resolution", Display.width * 0.5, Display.height * 0.25,
                                        screen=Display.screen, click_sound=False, x_adjust=True)

        if res_button:
            choose_resolution(start_menu)

        create_title_text("SFX Volume", color=(0, 0, 0), x=Display.width * 0.5, y=Display.height * 0.38,
                          screen=Display.screen, font=Fonts.med)

        create_title_text(f"{sound.sf_volume}", color=(0, 0, 0), x=Display.width * 0.5, y=Display.height * 0.45,
                          screen=Display.screen)

        plus_button = create_text_button(Fonts.xxl.font, "+", Display.width * 0.4, Display.height * 0.45,
                                         screen=Display.screen, click_sound=False, x_adjust=True)

        if plus_button:
            sound.change_sf_volume(1)
            Sound.thump.play()

        minus_button = create_text_button(Fonts.xxl.font, "-", Display.width * 0.6, Display.height * 0.45,
                                          screen=Display.screen, click_sound=False, x_adjust=True)

        if minus_button:
            sound.change_sf_volume(-1)
            Sound.thump.play()

        back_button = create_text_button(Fonts.lg.font, "Back", Display.width * 0.5, Display.height * 0.7,
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

    Game.active_background = Game.current_stage.background

    stage.player.place_initial_position()

    while True:

        Display.screen.fill((0, 0, 0))

        Game.active_background.center_on_screen()

        stage.user_interface()

        for evnt in pygame.event.get():
            Game.quit(evnt)
            stage.player.controls(evnt)
            if evnt.type == pygame.KEYUP:
                if evnt.key == pygame.K_ESCAPE:
                    stage.reset()
                    start_menu()
                if evnt.key == pygame.K_m:
                    sound.toggle_track()

        Game.current_stage.move_enemies()

        stage.player.move()
        stage.player.move_projectiles()

        stage.detect_collision()

        if not stage.enemy_list:  # Victory
            stage.is_complete = True
            stage.is_cleared = True
            stage.post_game_screen(f"STAGE {stage.stage_id} COMPLETE", Sound.victory, Images.victory)

        if stage.player.is_defeated:  # Defeat
            stage.post_game_screen("Game Over :(", Sound.defeat, Images.defeat)

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
