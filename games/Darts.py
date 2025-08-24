#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import random
import pygame

# ---------------- Window / Board sizing ----------------
WINDOW_W, WINDOW_H = 1280, 900
BOARD_DIAMETER = 720
R = BOARD_DIAMETER // 2

# Regulation-like proportions (as a fraction of the double-outer radius)
R_DOUBLE_OUTER = R
RING_WIDTH = int(R * 0.047)          # ≈8/170

R_DOUBLE_INNER = R_DOUBLE_OUTER - RING_WIDTH
R_TRIPLE_OUTER = int(R * 0.629)      # ≈107/170
R_TRIPLE_INNER = R_TRIPLE_OUTER - RING_WIDTH
R_BULL_OUTER   = int(R * 0.094)      # ≈16/170
R_BULL_INNER   = int(R * 0.037)      # ≈6.3/170

# ---------------- Colors ----------------
COL_BG         = (34, 34, 36)
COL_FACE       = (36, 36, 38)
COL_SINGLE_DK  = (40, 40, 40)         # wedge black
COL_SINGLE_LT  = (228, 219, 192)      # wedge cream
COL_RING_RED   = (196, 35, 35)
COL_RING_GRN   = (18, 145, 80)
COL_BULL_RED   = (200, 38, 38)
COL_BULL_GRN   = (12, 140, 78)
COL_LINE       = (240, 240, 240)
COL_EDGE       = (20, 20, 20)
COL_TEXT       = (245, 240, 220)
COL_ACCENT     = (255, 210, 70)
COL_LABEL_BG   = (0, 0, 0, 170)

# Number ring starting at 20 on top, clockwise
SECTOR_NUMBERS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]


# ---------- crisp annular-sector (no AA) ----------
def _annular_sector_points(cx, cy, r_outer, r_inner, a0, a1, steps=128):
    """Polygon points for a filled annular sector; curved edges via many short chords."""
    pts = []
    for i in range(steps + 1):                     # outer arc a0 -> a1
        a = a0 + (a1 - a0) * (i / steps)
        pts.append((int(cx + r_outer * math.cos(a)), int(cy + r_outer * math.sin(a))))
    for i in range(steps, -1, -1):                 # inner arc a1 -> a0
        a = a0 + (a1 - a0) * (i / steps)
        pts.append((int(cx + r_inner * math.cos(a)), int(cy + r_inner * math.sin(a))))
    return pts

def _fill_annular_sector(surf, color, cx, cy, r_outer, r_inner, a0, a1, steps=128):
    pygame.draw.polygon(surf, color, _annular_sector_points(cx, cy, r_outer, r_inner, a0, a1, steps), 0)


# ---------------- Board drawing (sharp) ----------------
def draw_dartboard(surface, center):
    """Render a sharp, realistic dartboard centered at 'center' (20 at top)."""
    cx, cy = center
    FUDGE = 1  # px overlap so adjacent colors meet cleanly (no hairline seams)

    # Base and outer bevel (plain circles are crisp)
    pygame.draw.circle(surface, COL_FACE, center, R_DOUBLE_OUTER + 10)
    pygame.draw.circle(surface, COL_EDGE, center, R_DOUBLE_OUTER + 10, 10)

    # Singles first (paint entire base with wedges)
    for i in range(20):
        a0 = math.radians(i * 18 - 9 - 90)
        a1 = math.radians((i + 1) * 18 - 9 - 90)
        single_color = COL_SINGLE_DK if i % 2 == 0 else COL_SINGLE_LT  # 20 is dark
        # Outer single: triple_outer..double_inner
        _fill_annular_sector(surface, single_color, cx, cy, R_DOUBLE_INNER, R_TRIPLE_OUTER, a0, a1)
        # Inner single: bull_outer..triple_inner
        _fill_annular_sector(surface, single_color, cx, cy, R_TRIPLE_INNER, R_BULL_OUTER, a0, a1)

    # Triple & Double rings (overlay with tiny overlap fudge for perfect joins)
    for i in range(20):
        a0 = math.radians(i * 18 - 9 - 90)
        a1 = math.radians((i + 1) * 18 - 9 - 90)
        col = COL_RING_RED if i % 2 == 0 else COL_RING_GRN
        _fill_annular_sector(surface, col, cx, cy, R_TRIPLE_OUTER + FUDGE, R_TRIPLE_INNER - FUDGE, a0, a1)
        _fill_annular_sector(surface, col, cx, cy, R_DOUBLE_OUTER,       R_DOUBLE_INNER - FUDGE, a0, a1)

    # Bulls (draw last so they’re crisp and overlap the inner single edge)
    pygame.draw.circle(surface, COL_BULL_GRN, center, R_BULL_OUTER + FUDGE)
    pygame.draw.circle(surface, COL_BULL_RED, center, R_BULL_INNER)

    # Outer rim
    pygame.draw.circle(surface, COL_LINE, center, R_DOUBLE_OUTER, 3)

    # Numbers ring (little white circles with numbers)
    num_font = pygame.font.SysFont("Arial", 34, bold=True)
    for i, num in enumerate(SECTOR_NUMBERS):
        ang = math.radians(i * 18 - 90)
        r_text = R_DOUBLE_OUTER + 36
        x, y = cx + r_text * math.cos(ang), cy + r_text * math.sin(ang)
        pygame.draw.circle(surface, COL_EDGE, (int(x), int(y)), 24)
        pygame.draw.circle(surface, COL_LINE, (int(x), int(y)), 24, 3)
        text = num_font.render(str(num), True, COL_LINE)
        rect = text.get_rect(center=(x, y))
        surface.blit(text, rect)


# ---------------- Scoring ----------------
def score_from_point(center, pos):
    """Return (points, multiplier, sector_number, ring_label) for the dart at pos."""
    cx, cy = center
    px, py = pos
    dx, dy = px - cx, py - cy
    r = math.hypot(dx, dy)

    if r > R_DOUBLE_OUTER:
        return 0, 0, 0, "MISS"
    if r <= R_BULL_INNER:
        return 50, 0, 50, "BULL"
    if r <= R_BULL_OUTER:
        return 25, 0, 25, "OUTER BULL"

    ang = (math.degrees(math.atan2(dy, dx)) + 90.0) % 360.0
    sector_index = int(((ang + 9.0) % 360.0) // 18.0)
    sector_number = SECTOR_NUMBERS[sector_index]

    if R_TRIPLE_INNER < r <= R_TRIPLE_OUTER:
        return sector_number * 3, 3, sector_number, f"T{sector_number}"
    if R_DOUBLE_INNER < r <= R_DOUBLE_OUTER:
        return sector_number * 2, 2, sector_number, f"D{sector_number}"
    return sector_number, 1, sector_number, f"{sector_number}"


# ---------------- HQ 180 celebration (human waving poster) ----------------
def _rotate_point(px, py, cx, cy, theta):
    s, c = math.sin(theta), math.cos(theta)
    px -= cx; py -= cy
    return px * c - py * s + cx, px * s + py * c + cy

def make_180_frames_hq(width=900, height=520, n_frames=48, ss=2):
    """
    Supersampled (ss×) human waving a '180' poster left/right with confetti + flashes.
    Returns a list of pygame.Surface frames at (width, height).
    """
    frames = []
    rng = random.Random(180)

    W, H = width * ss, height * ss
    cx, ground = W // 2, int(H * 0.90)
    shoulder_y = int(H * 0.52)
    shoulder_dx = 120
    head_r = 52
    torso_w = 180

    poster_w, poster_h = 820, 380
    y_poster = shoulder_y - 120
    amp = int(W * 0.15)              # horizontal waving amplitude
    rot_amp = math.radians(12)       # rotation amplitude
    big = pygame.font.SysFont("Impact", 320, bold=True)

    # Prebuild unrotated poster (with drop shadow + gloss)
    base = pygame.Surface((poster_w, poster_h), pygame.SRCALPHA)
    # card
    pygame.draw.rect(base, (250, 250, 250), (0, 0, poster_w, poster_h), border_radius=28)
    pygame.draw.rect(base, (20, 20, 22), (0, 0, poster_w, poster_h), width=10, border_radius=28)
    # stripes
    pygame.draw.rect(base, COL_RING_GRN, (0, 30, poster_w, 24), border_radius=12)
    pygame.draw.rect(base, COL_RING_RED, (0, poster_h - 54, poster_w, 24), border_radius=12)
    # gloss
    gloss = pygame.Surface((poster_w, poster_h // 2), pygame.SRCALPHA)
    pygame.draw.ellipse(gloss, (255, 255, 255, 40), (-20, -poster_h // 4, poster_w + 40, poster_h))
    base.blit(gloss, (0, 0))
    # 180
    txt = big.render("180", True, (20, 20, 22))
    base.blit(txt, txt.get_rect(center=(poster_w // 2, poster_h // 2)))

    # separate poster shadow
    shadow = pygame.Surface((poster_w + 160, poster_h + 160), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 120),
                        (0, poster_h, poster_w + 160, 80))

    for i in range(n_frames):
        t = i / (n_frames - 1)
        phase = math.sin(t * 2 * math.pi)
        px = cx + int(amp * phase)
        theta = rot_amp * phase

        frame = pygame.Surface((W, H), pygame.SRCALPHA)

        # crowd silhouette
        for x in range(0, W, 52):
            pygame.draw.circle(frame, (18, 18, 22, 255), (x + rng.randint(-4, 4), ground + 10), 40)
        for x in range(26, W, 64):
            pygame.draw.circle(frame, (12, 12, 15, 255), (x + rng.randint(-6, 6), ground - 10), 54)

        # human body (shadow)
        pygame.draw.ellipse(frame, (0, 0, 0, 80), (cx - 180, ground - 20, 360, 40))

        # legs
        pygame.draw.rect(frame, (28, 28, 33), (cx - 44, ground - 180, 36, 180))
        pygame.draw.rect(frame, (28, 28, 33), (cx + 8, ground - 180, 36, 180))
        # torso
        pygame.draw.rect(frame, (36, 36, 42), (cx - torso_w // 2, shoulder_y + 40, torso_w, 160), border_radius=20)
        # head
        pygame.draw.circle(frame, (220, 195, 160), (cx, shoulder_y), head_r)
        pygame.draw.circle(frame, (0, 0, 0), (cx - 16, shoulder_y - 6), 6)
        pygame.draw.circle(frame, (0, 0, 0), (cx + 16, shoulder_y - 6), 6)
        pygame.draw.arc(frame, (0, 0, 0), (cx - 24, shoulder_y + 6, 48, 24), math.pi, 2 * math.pi, 3)

        # rotate poster
        poster_rot = pygame.transform.rotate(base, math.degrees(theta))
        pr = poster_rot.get_rect(center=(px, y_poster))
        # shadow under poster
        frame.blit(shadow, (pr.x - 80, pr.y + poster_h // 2))
        frame.blit(poster_rot, pr.topleft)

        # corners for arms after rotation
        tl = _rotate_point(pr.centerx - poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        tr = _rotate_point(pr.centerx + poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        left_shoulder = (cx - shoulder_dx, shoulder_y + 80)
        right_shoulder = (cx + shoulder_dx, shoulder_y + 80)

        # arms + hands
        pygame.draw.line(frame, (32, 32, 36), left_shoulder, tl, 28)
        pygame.draw.line(frame, (32, 32, 36), right_shoulder, tr, 28)
        pygame.draw.circle(frame, (22, 22, 26), (int(tl[0]), int(tl[1])), 16)
        pygame.draw.circle(frame, (22, 22, 26), (int(tr[0]), int(tr[1])), 16)

        # confetti
        rng2 = random.Random(1000 + i)
        for _ in range(220):
            c = rng2.choice([COL_RING_RED, COL_RING_GRN, COL_ACCENT, (240, 240, 240)])
            pygame.draw.circle(frame, c, (rng2.randrange(W), rng2.randrange(int(H * 0.85))), rng2.randrange(2, 5))

        # camera flashes near the wave extremes
        flash = abs(phase)
        if flash > 0.93:
            alpha = int(180 * ((flash - 0.93) / 0.07))
            f = pygame.Surface((W, H), pygame.SRCALPHA)
            f.fill((255, 255, 255, max(0, min(255, alpha))))
            frame.blit(f, (0, 0))

        # downsample for crisp AA overall
        frame = pygame.transform.smoothscale(frame, (width, height))
        frames.append(frame)

    return frames


# ---------------- Simple 501 game scaffold ----------------
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 501
        self.throws_this_turn = 0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Darts – realistic board (20 on top)")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()

        # Center the board in the middle of the window
        self.cx, self.cy = WINDOW_W // 2, WINDOW_H // 2

        # Pre-render the board onto a surface (saves CPU)
        self.board_surface = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        draw_dartboard(self.board_surface, (self.cx, self.cy))

        self.players = [Player(f"Player {i}") for i in range(1, 5)]
        self.turn = 0
        self.max_throws = 3

        # Per-turn, current player only
        self.turn_hits = []        # list of (pos, points, mult, label)
        self.turn_points = []      # numeric points for this turn

        self.font_big = pygame.font.SysFont("Arial", 36, bold=True)
        self.font = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_huge = pygame.font.SysFont("Impact", 64, bold=True)

        # HQ 180 animation
        self.frames_180 = make_180_frames_hq()
        self.anim180_on = False
        self.anim180_index = 0
        self.anim180_loops = 0
        self.anim180_max_loops = 2
        self.anim180_timer = 0
        self.anim180_interval = 38  # ms

    def next_player(self):
        self.players[self.turn].throws_this_turn = 0
        self.turn_points.clear()
        self.turn_hits.clear()
        self.turn = (self.turn + 1) % len(self.players)

    def draw_ui(self):
        self.screen.fill(COL_BG)
        self.screen.blit(self.board_surface, (0, 0))

        p = self.players[self.turn]
        header = self.font_big.render(f"{p.name} — throws left: {self.max_throws - p.throws_this_turn}", True, COL_TEXT)
        self.screen.blit(header, (24, 24))

        # scoreboard (top-right)
        x0 = WINDOW_W - 320
        title = self.font_big.render("SCORES", True, COL_TEXT)
        self.screen.blit(title, (x0, 24))
        for i, pl in enumerate(self.players):
            y = 70 + i * 36
            label = self.font.render(f"{pl.name}:", True, COL_TEXT)
            val = self.font.render(str(pl.score), True, COL_ACCENT if i == self.turn else COL_TEXT)
            self.screen.blit(label, (x0, y))
            self.screen.blit(val, (x0 + 160, y))

        # Current player's dots only
        for (x, y), s, m, lab in self.turn_hits[-9:]:
            pygame.draw.circle(self.screen, COL_ACCENT, (x, y), 6)

        # Last shot label (HUD + near dart)
        if self.turn_hits:
            (lx, ly), s, m, lab = self.turn_hits[-1]
            hud = self.font.render(f"Last: {s} ({lab})", True, COL_TEXT)
            self.screen.blit(hud, (24, 64))

            txt = self.font_small.render(f"{s} ({lab})", True, COL_TEXT)
            pad = 6
            rect = txt.get_rect()
            rect.topleft = (lx + 12, ly - rect.height - 8)
            rect.x = min(max(rect.x, 8), WINDOW_W - rect.width - 8)
            rect.y = min(max(rect.y, 8), WINDOW_H - rect.height - 8)
            bubble = pygame.Surface((rect.width + pad*2, rect.height + pad*2), pygame.SRCALPHA)
            bubble.fill(COL_LABEL_BG)
            self.screen.blit(bubble, (rect.x - pad, rect.y - pad))
            self.screen.blit(txt, rect.topleft)

        footer = self.font.render(
            "Click board to throw • R = reset current player • N = next player • Esc = quit",
            True, COL_TEXT
        )
        self.screen.blit(footer, (24, WINDOW_H - 36))

        # ---- 180 celebration overlay ----
        if self.anim180_on:
            dim = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 160))
            self.screen.blit(dim, (0, 0))

            frame = self.frames_180[self.anim180_index]
            rect = frame.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 40))
            self.screen.blit(frame, rect.topleft)

            banner = self.font_huge.render("ONE HUNDRED AND EIGHTY!", True, (255, 255, 255))
            self.screen.blit(banner, banner.get_rect(center=(WINDOW_W // 2, rect.top - 28)))

    def trigger_180_animation(self):
        self.anim180_on = True
        self.anim180_index = 0
        self.anim180_loops = 0
        self.anim180_timer = pygame.time.get_ticks()

    def step_animation(self):
        if not self.anim180_on:
            return
        now = pygame.time.get_ticks()
        if now - self.anim180_timer >= self.anim180_interval:
            self.anim180_timer = now
            self.anim180_index += 1
            if self.anim180_index >= len(self.frames_180):
                self.anim180_index = 0
                self.anim180_loops += 1
                if self.anim180_loops >= self.anim180_max_loops:
                    self.anim180_on = False

    def handle_throw(self, pos):
        p = self.players[self.turn]
        if p.throws_this_turn >= self.max_throws:
            return
        score, mult, sect, label = score_from_point((self.cx, self.cy), pos)

        # Basic 501: ignore busts that would take score below zero
        if p.score - score >= 0:
            p.score -= score
            p.throws_this_turn += 1
            self.turn_hits.append((pos, score, mult, label))
            self.turn_points.append(score)

            # 180 celebration
            if len(self.turn_points) == 3 and sum(self.turn_points) == 180:
                self.trigger_180_animation()

        if p.score == 0 or p.throws_this_turn >= self.max_throws:
            self.next_player()

    def run(self):
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    self.players[self.turn].score = 501
                    self.players[self.turn].throws_this_turn = 0
                    self.turn_hits.clear()
                    self.turn_points.clear()
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_n:
                    self.next_player()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.handle_throw(e.pos)

            self.step_animation()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# --------- ENTRY POINT (for external launcher) ----------
def main():
    Game().run()


if __name__ == "__main__":
    main()
