import math
import random
from collections import defaultdict, namedtuple
from enum import IntEnum

import hmsysteme
import pygame
from pygame.constants import (
    K_ESCAPE,
    K_RETURN,
    KEYDOWN,
    KEYUP,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    QUIT,
)

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
RED = (255, 0, 0)


# Font sizes
FONT_SIZE_NORMAL = 60
FONT_SIZE_BIG = 100

# FPS
FPS_INSTRUCTIONS = 20
FPS_GAME = 80
FPS_QUIT = 5

# Score punishments (defaults, can be overridden per GameInfo)
PUNISH_HARD = 500
PUNISH_SOFT = 100

# Target sizing and placement
TARGET_RADIUS_FACTOR = 0.4  # fraction of min(screen_w, screen_h)
TARGET_POS_X_MIN_FACTOR = 0.2
TARGET_POS_X_MAX_FACTOR = 0.8
TARGET_POS_Y_MIN_FACTOR = 0.35
TARGET_POS_Y_MAX_FACTOR = 0.65

# Target timing (milliseconds)
TARGET_TIME_BEFORE_SHRINK = 2000
TARGET_TIME_SHRINKING = 7000
TARGET_TIME_AFTER = 2000
TARGET_TIME_SCREENSHOT = 500

# Bullet hole visuals / timing (milliseconds)
BULLETHOLE_RADIUS = 25
BULLETHOLE_SHRINKING_TIME = 3000

# Default game parameters (used in main as fallback)
DEFAULT_NUMBER_OF_TARGETS = 2
DEFAULT_NUMBER_OF_ROUNDS = 2


class TargetState(IntEnum):  # State for Target
    NEW = 1
    BEFORE_SHRINK = 2
    SHRINK = 3
    AFTER = 4
    EXIT = 5


class PlayerState(IntEnum):  # State for Target
    NEW = 1
    RUNNING = 2
    NEXT_TARGET = 3
    NEXT_ROUND = 4
    WAIT_NEXT_ROUND = 5
    GAME_OVER = 6


class AppState(IntEnum):
    STARTUP = 1
    INSTRUCTIONS = 2
    GAME = 3
    HIGHSCORE = 4
    QUIT_GAME = 5
    EXIT = 6


class GameInfo:
    def __init__(
        self,
        screen_size: tuple,
        number_of_rounds: int,
        number_of_targets: int,
        playernames: list,
        wait_enter: bool = True,
    ):
        self.screen_size = screen_size
        # self.screen = pygame.display.set_mode(self.screen_size)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.number_of_rounds = number_of_rounds
        self.number_of_targets = number_of_targets

        self.playernames = playernames
        self.wait_enter = wait_enter
        self.hard_punish = PUNISH_HARD
        self.soft_punish = PUNISH_SOFT

        self.current_player = None

        self.delay = 0

        pygame.font.init()
        self.font = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.font_big = pygame.font.Font(None, FONT_SIZE_BIG)


class App:
    def __init__(self, gameinfo, debug: bool = False):
        self.debug = debug
        self.gameinfo = gameinfo
        self.fps = FPS_INSTRUCTIONS

        self.state = AppState.STARTUP
        self.old_state = AppState.STARTUP
        self.clock = pygame.time.Clock()

        self.screen_color = WHITE
        self.caption = ""
        self.old_caption = None

        self.players = []
        self.player_index = 0
        for name in self.gameinfo.playernames:
            self.players.append(Player(name, self.gameinfo))
        self.player = self.players[self.player_index]

        self.all_scores = []

        self.next_state()

    def next_state(self):
        if self.state == AppState.STARTUP:
            self.state = AppState.INSTRUCTIONS
        elif self.state == AppState.INSTRUCTIONS:
            self.state = AppState.GAME
        elif self.state == AppState.GAME:
            self.state = AppState.HIGHSCORE
            self.get_all_scores()
        elif self.state == AppState.HIGHSCORE:
            self.state = AppState.EXIT
        else:
            print("App next_state else!?")

    def get_all_scores(self):  # ToDo
        print("\nResults")
        print("Player\t", end="")
        for player in self.players:
            print(player.name, end="\t")
        print("")

        for round_no in range(self.gameinfo.number_of_rounds):
            for target_no in range(self.gameinfo.number_of_targets):
                print("R{} T{}\t".format(round_no, target_no), end="")
                for player in self.players:
                    score = str(player.targets[round_no][target_no].score)
                    print(score + "\t", end="")
                print("")

            print("Subtot\t", end="")
            for player in self.players:
                summe = str(
                    [
                        sum([y.score for y in x.values()])
                        for x in player.targets.values()
                    ][round_no]
                )
                print(summe + "\t", end="")
            print("")
            print("---\t" * (len(self.players) + 1))

        print("Final\t", end="")
        for player in self.players:
            summe = str(
                sum(
                    [
                        sum([y.score for y in x.values()])
                        for x in player.targets.values()
                    ]
                )
            )
            print(summe + "\t", end="")

            # for (no_round, no_target), target in player.targets.items():
            # print("R{}T{}: {}".format(no_round + 1, no_target + 1, target.score))
            # self.all_scores.append([player.name, no_round, no_target, target.score])

        # print(tabulate(self.all_scores))
        # print("Summe: {}".format(sum([target.score for a, target in player.targets.items()])))

    def escape_action(self):
        if self.state == AppState.QUIT_GAME:
            self.state = AppState.EXIT
        else:
            self.old_state = self.state
            self.state = AppState.QUIT_GAME

    def return_action(self):
        if self.state == AppState.INSTRUCTIONS:
            self.next_state()
        elif self.state == AppState.GAME:
            self.player.push_enter()
        elif self.state == AppState.HIGHSCORE:
            self.next_state()
        elif self.state == AppState.QUIT_GAME:
            self.state = self.old_state
        else:
            pass

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = AppState.QUIT_GAME
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.escape_action()
                elif event.key == K_RETURN:
                    self.return_action()
            elif event.type == MOUSEBUTTONUP:
                if self.debug:
                    xy = pygame.mouse.get_pos()
                    if self.state == AppState.GAME:
                        self.player.create_bullet_hole(xy)

        if hmsysteme.hit_detected():
            (x, y) = hmsysteme.get_pos()
            if self.state == AppState.GAME:
                self.player.create_bullet_hole((int(x), int(y)))

        iGetAction = hmsysteme.get_action()
        if iGetAction > 0:
            # Button 10m Pistole
            if iGetAction == 1:
                self.state = AppState.QUIT_GAME
            elif iGetAction == 3:
                self.return_action()

    def update(self, dt):
        if self.state == AppState.INSTRUCTIONS:
            pass

        elif self.state == AppState.GAME:
            self.player.update(dt)
            player_state = self.player.state

            if player_state == PlayerState.RUNNING:
                pass

            # one Target is gone
            elif player_state == PlayerState.NEXT_TARGET:
                pass

            # Round over / next Player
            elif player_state == PlayerState.NEXT_ROUND:
                self.player_index += 1

                if self.player_index < len(self.players):
                    self.player = self.players[self.player_index]

                else:  # no more Players / next Round
                    self.player_index = 0
                    self.player = self.players[self.player_index]

            # All Players have played, new Round, activate Player
            elif player_state == PlayerState.WAIT_NEXT_ROUND:
                self.player.state = PlayerState.RUNNING
                #
            # Player done, next player or Quit()
            elif player_state == PlayerState.GAME_OVER:
                self.player_index += 1

                if self.player_index < len(self.players):
                    self.player = self.players[self.player_index]

                else:  # Quit
                    self.next_state()

        elif self.state == AppState.HIGHSCORE:
            pass

    def draw(self):
        if self.state == AppState.INSTRUCTIONS:
            self.fps = FPS_INSTRUCTIONS
            self.screen_color = GRAY
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "Instructions"

            lines = [
                "Willkommen zu FPShooter.",
                "",
                f"Das schwarze Ziel wird mit der Zeit ({TARGET_TIME_SHRINKING / 1000}s) immer kleiner.",
                "Je später du das Ziel triffst, desto WENIGER Punkte bekommst du.",
                f"Warte aber nicht zu lange, sonst ist es weg und du bekommst {PUNISH_HARD} Strafpunkte.",
                f"Wenn du daneben schießt, bekommst du {PUNISH_SOFT} Punkte dazu.",
                "",
                f"Es werden {DEFAULT_NUMBER_OF_ROUNDS} Runden mit jeweils {DEFAULT_NUMBER_OF_TARGETS} Zielen gespielt.",
                "Alle Mitspieler schießen nacheinander.",
                "Wer zum Schluss die WENIGSTEN Punkte hat gewinnt!",
            ]
            for number, line in enumerate(lines):
                font_surf = self.gameinfo.font.render(line, True, WHITE)
                font_rect = font_surf.get_rect(topleft=(25, number * 60 + 200))
                self.gameinfo.screen.blit(font_surf, font_rect)

        elif self.state == AppState.GAME:
            self.fps = FPS_GAME
            self.screen_color = WHITE
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "FPShooter"

            self.player.draw()

            name = self.player.name
            name_text = self.gameinfo.font.render("{}".format(name), True, BLACK, WHITE)
            self.gameinfo.screen.blit(name_text, [40, 100])

            score = self.player.score
            score_text = self.gameinfo.font.render(
                "Punkte: {}".format(score), True, BLACK, WHITE
            )
            self.gameinfo.screen.blit(
                score_text, [40, self.gameinfo.screen_size[1] - 100]
            )

        elif self.state == AppState.HIGHSCORE:
            pass
            self.fps = FPS_INSTRUCTIONS
            self.screen_color = GRAY
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "Highscore"
            """
            x = self.gameinfo.screen_size[0] / 2
            offset = 0
            for player in self.players:
                name = self.gameinfo.font.render("Player: {}".format(player.name), True, BLACK)
                self.gameinfo.screen.blit(name, (int(x - name.get_width() / 2), int((name.get_height()) + offset)))

                offset += 50

                for (no_round, no_target), target in player.targets.items():

                    score = self.gameinfo.font.render("Runde {} Scheibe {}, Punkte: {}".format(no_round + 1 , no_target + 1, target.score), True, BLACK)

                    self.gameinfo.screen.blit(score, (int(x - score.get_width() / 2), int((score.get_height()) + offset)))

                    offset += 50

                summ = self.gameinfo.font.render("Summe: {}".format(sum([target.score for a, target in player.targets.items()])), True, BLACK)
                self.gameinfo.screen.blit(summ, (int(x - summ.get_width() / 2), int((summ.get_height()) + offset)))

                offset += 80
            """

        elif self.state == AppState.QUIT_GAME:
            #
            self.fps = FPS_QUIT
            self.screen_color = BLACK
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "Spiel beenden"
            text_quit_1 = self.gameinfo.font.render("Spiel beenden?", True, WHITE)
            text_quit_2 = self.gameinfo.font.render("Bestätigen mit Esc", True, WHITE)
            text_quit_3 = self.gameinfo.font.render("Zurück mit Enter", True, WHITE)

            self.gameinfo.screen.blit(text_quit_1, [200, 200])
            self.gameinfo.screen.blit(
                text_quit_2, [200, 200 + self.gameinfo.font.get_height() * 1.5]
            )
            self.gameinfo.screen.blit(
                text_quit_3, [200, 200 + 2 * self.gameinfo.font.get_height() * 1.5]
            )

        if self.caption != self.old_caption:
            self.old_caption = self.caption
            pygame.display.set_caption(self.caption)

    def run(self):
        while not self.state == AppState.EXIT:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()


class Player:
    def __init__(self, name, gameinfo):
        self.gameinfo = gameinfo
        self.name = name
        self.state = PlayerState.RUNNING
        self.score = 0
        self.number_of_rounds = self.gameinfo.number_of_rounds
        self.number_of_targets = self.gameinfo.number_of_targets
        self.current_round = 0
        self.current_target = 0
        self.targets = defaultdict(dict)  # No. Target / Round

        for round_number in range(self.number_of_rounds):
            for target_number in range(self.number_of_targets):
                self.targets[round_number][target_number] = Target(self.gameinfo)

        self.target = self.targets[self.current_round][self.current_target]

    def push_enter(self):
        self.target.push_enter()

    def update(self, dt):
        if self.state == PlayerState.NEW:
            pass

        elif self.state == PlayerState.RUNNING:
            self.target.update(dt)

            # self.score = sum([x.score for x in self.targets.values()])
            sum_per_round = [
                sum([y.score for y in x.values()]) for x in self.targets.values()
            ]
            self.score = sum(sum_per_round)

            if self.target.properties().state == TargetState.EXIT:
                self.state = PlayerState.NEXT_TARGET

        elif self.state == PlayerState.NEXT_TARGET:
            self.current_target += 1
            if self.current_target < self.number_of_targets:  # next Target -> Running
                self.target = self.targets[self.current_round][self.current_target]
                self.state = PlayerState.RUNNING
            else:  # no more Targets -> Round Over
                self.state = PlayerState.NEXT_ROUND

        elif self.state == PlayerState.NEXT_ROUND:
            self.current_target = 0
            self.current_round += 1
            if self.current_round < self.number_of_rounds:  # next
                self.target = self.targets[self.current_round][self.current_target]
                self.state = PlayerState.WAIT_NEXT_ROUND
            else:
                self.state = PlayerState.GAME_OVER

        elif self.state == PlayerState.WAIT_NEXT_ROUND:
            pass  # wait for reset to Running

        elif self.state == PlayerState.GAME_OVER:
            pass

        else:
            print("PlayerState Else?!")
            print(self.state)

    def draw(self):
        self.target.draw()

        if self.target.state == TargetState.NEW:
            player_1 = self.gameinfo.font_big.render(
                "Player: {}".format(self.name), True, BLACK
            )
            player_2 = self.gameinfo.font.render("Press Enter", True, BLACK)
            x = self.gameinfo.screen_size[0] / 2
            y = self.gameinfo.screen_size[1] / 2
            self.gameinfo.screen.blit(
                player_1,
                (int(x - player_1.get_width() / 2), int(y - player_1.get_height() / 2)),
            )
            self.gameinfo.screen.blit(
                player_2,
                (
                    int(x - player_2.get_width() / 2),
                    int((y - player_2.get_height() / 2) + 75),
                ),
            )

    def create_bullet_hole(self, xy):
        self.target.new_hole(xy)


class Target:
    def __init__(self, gameinfo):
        self.gameinfo = gameinfo

        min_screen = min(self.gameinfo.screen_size[0], self.gameinfo.screen_size[1])
        self.radius_original = int(min_screen * TARGET_RADIUS_FACTOR)
        self.radius = self.radius_original

        self.timer = TARGET_TIME_BEFORE_SHRINK
        self.timer_screenshot = TARGET_TIME_SCREENSHOT

        self.wait_enter = self.gameinfo.wait_enter

        self.state = TargetState.NEW
        self.color = RED
        self.make_screenshot = False  # timer starts, gets updated in update()

        self.x = random.randint(
            int(gameinfo.screen_size[0] * TARGET_POS_X_MIN_FACTOR),
            int(gameinfo.screen_size[0] * TARGET_POS_X_MAX_FACTOR),
        )
        self.y = random.randint(
            int(gameinfo.screen_size[1] * TARGET_POS_Y_MIN_FACTOR),
            int(gameinfo.screen_size[1] * TARGET_POS_Y_MAX_FACTOR),
        )

        self.score = 0

        self.holes = []

    def push_enter(self):
        self.wait_enter = False

    def draw(self):
        pygame.draw.circle(
            self.gameinfo.screen, self.color, (self.x, self.y), int(self.radius), 0
        )
        # current_radius = self.gameinfo.font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        # self.gameinfo.screen.blit(current_radius, [10, self.gameinfo.screen_size[1] - 45])

        for hole in self.holes:
            hole.draw()

    def calculate_score(self):
        self.score = sum([x.score for x in self.holes])

    def new_hole(self, xy):
        if self.state == TargetState.NEW:  # Hit while waiting for Enter (Return) Button
            self.state = TargetState.BEFORE_SHRINK
            self.timer = TARGET_TIME_BEFORE_SHRINK

        elif self.state == TargetState.BEFORE_SHRINK:  # Hit before Target is black
            self.holes.append(
                Bullet_Hole(self.gameinfo, xy, RED, self.gameinfo.hard_punish)
            )
            self.state = TargetState.AFTER
            self.timer = TARGET_TIME_AFTER

        elif self.state == TargetState.SHRINK:  # Hit while shrinking
            x, y = xy
            if self.gameinfo.delay > 0:
                additional = int(
                    (self.gameinfo.delay / TARGET_TIME_SHRINKING) * self.radius_original
                )
            else:
                additional = 0

            distance = math.dist((self.x, self.y), (x, y))
            if distance <= self.radius:  # Hit
                self.holes.append(
                    Bullet_Hole(self.gameinfo, xy, GREEN, int(self.radius) + additional)
                )
                # keep radius consistent (radius was shrinking; restore extra if delay)
                self.radius += additional
                print(
                    f"Spieler: Radius:{self.radius:0.2f}\n",
                    f"Hit distance from center:{distance:0.2f}\n",
                    "Hit!\n",
                    f"{distance - self.radius:0.3f} from corner\n\n",
                )

            else:  # Miss
                self.holes.append(
                    Bullet_Hole(self.gameinfo, xy, RED, self.gameinfo.soft_punish)
                )
                print(
                    f"Radius:{self.radius:0.2f}\n",
                    f"Hit distance from center:{distance:0.2f}\n",
                    "Miss!\n",
                    f"{distance - self.radius:0.3f} Pixel outside :(\n\n",
                )
            self.state = TargetState.AFTER
            self.timer = TARGET_TIME_AFTER

        elif self.state == TargetState.AFTER:
            self.holes.append(
                Bullet_Hole(self.gameinfo, xy, RED, self.gameinfo.hard_punish)
            )

        else:
            print("create bullet hole - else?")

        self.calculate_score()
        self.make_screenshot = True

    def properties(self):
        target = namedtuple("target", ["state", "x", "y", "radius"])
        return target(self.state, self.x, self.y, self.radius)

    def update(self, dt):
        if self.state == TargetState.NEW:
            if self.wait_enter:  # Wait for ENTER (Return) to be pushed
                pass
            else:
                self.wait_enter = True if self.gameinfo.wait_enter else False
                self.state = TargetState.BEFORE_SHRINK
                self.timer = TARGET_TIME_BEFORE_SHRINK

        elif self.state == TargetState.BEFORE_SHRINK:
            self.timer -= dt
            # color fade to black
            val = int(max(0, min(254, (self.timer / TARGET_TIME_BEFORE_SHRINK) * 254)))
            self.color = (val, 0, 0)
            if self.timer <= 0:
                self.state = TargetState.SHRINK
                self.color = BLACK
                self.timer = TARGET_TIME_SHRINKING

        elif self.state == TargetState.SHRINK:
            self.timer -= dt
            if self.timer > -(self.gameinfo.delay) - dt:
                self.radius = (
                    self.timer / TARGET_TIME_SHRINKING
                ) * self.radius_original
                self.radius = 0 if self.radius <= 0 else self.radius
                # print("dt: {}, timer: {:1.2f}, radius: {:1.2f}, andere: {:1.4f}".format(dt,self.timer, self.radius, 1-(TARGET_SHRINKING_TIME - self.timer)/TARGET_SHRINKING_TIME))
            else:
                self.state = TargetState.AFTER
                self.timer = TARGET_TIME_AFTER
                bullet_hole = Bullet_Hole(
                    self.gameinfo,
                    xy=(self.x, self.y),
                    color=RED,
                    score=self.gameinfo.hard_punish,
                )
                self.holes.append(bullet_hole)
                # self.holes.append(Bullet_Hole(self.x, self.y, RED, self.gameinfo.hard_punish))

        elif self.state == TargetState.AFTER:
            self.timer -= dt
            if self.timer > 0:
                pass
            else:
                self.state = TargetState.EXIT
                for hole in self.holes:
                    hole.display = False

        elif self.state == TargetState.EXIT:
            pass

        else:
            print("else?")

        for hole in self.holes:
            hole.update(dt)

        self.calculate_score()

        if self.make_screenshot:
            self.timer_screenshot -= dt
            if self.timer_screenshot <= 0:
                self.make_screenshot = False
                self.timer_screenshot = TARGET_TIME_SCREENSHOT
                hmsysteme.take_screenshot(self.gameinfo.screen)


class Bullet_Hole:
    def __init__(self, gameinfo, xy=(0, 0), color=RED, score=0):
        self.gameinfo = gameinfo

        self.radius = BULLETHOLE_RADIUS
        self.timer = BULLETHOLE_SHRINKING_TIME

        (self.x, self.y) = xy

        self.color = color
        self.score = score
        self.score_position = 0
        self.display = True
        self.score_surface = self.gameinfo.font.render(
            str(self.score), True, self.color
        )
        # print(self.__dict__)

    def update(self, dt):
        if self.display:
            if self.timer > 0:
                self.timer -= dt
                if self.timer < 0:
                    self.timer = 0
                self.radius = (
                    self.timer / BULLETHOLE_SHRINKING_TIME
                ) * BULLETHOLE_RADIUS
                self.score_position -= 0.5
            else:
                self.display = False

    def draw(self):
        if self.display:
            pygame.draw.circle(
                self.gameinfo.screen, self.color, (self.x, self.y), int(self.radius), 0
            )
            self.gameinfo.screen.blit(
                self.score_surface, [self.x + 25, self.y + int(self.score_position)]
            )


def main(debug: bool = False):
    pygame.init()

    playernames = hmsysteme.get_playernames()
    if not playernames:
        playernames = ["a", "b"]

    screen_size = (800, 600)
    if debug:
        modes = pygame.display.list_modes()
        if modes:
            screen_size = modes[0]  # Default to highest resolution
    else:
        screen_size = hmsysteme.get_size()

    print(screen_size)

    hmsysteme.put_button_names(["Escape", "no function", "Enter"])

    number_of_targets = DEFAULT_NUMBER_OF_TARGETS  # Targets per player
    number_of_rounds = DEFAULT_NUMBER_OF_ROUNDS  # Number of Rounds
    wait_enter = True  # Wait for enter button to be pushed

    gameinfo = GameInfo(
        screen_size, number_of_rounds, number_of_targets, playernames, wait_enter
    )

    app = App(gameinfo, debug=debug)
    app.run()

    pygame.quit()


if __name__ == "__main__":
    main(debug=True)
