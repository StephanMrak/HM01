#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import pygame

# =========================== Config ===================================
LOW_POWER = True            # Low-power animation path for Pi Zero 2
WINDOW_W, WINDOW_H = 1280, 900
BOARD_DIAMETER = 720
FPS_IDLE = 30               # frame cap when idle
FPS_ANIM = 48               # frame cap during 180 animation
DEPTH_16BIT = True          # 16-bit mode can be faster on Pi
FULLSCREEN = False          # set True on Pi for best performance

# ===================== Optional hardware (hmsysteme) ==================
try:
    import hmsysteme
    HAVE_HW = True
except Exception:
    hmsysteme = None
    HAVE_HW = False

def hw_poll():
    """
    Adapter over a few possible hmsysteme APIs.
    Returns (hit:bool, (x, y):tuple[int,int]).
    Safe to call every loop; very light.
    """
    if not HAVE_HW:
        return False, (0, 0)
    try:
        if hasattr(hmsysteme, "hit_detected") and hmsysteme.hit_detected():
            if hasattr(hmsysteme, "get_pos"):
                return True, tuple(map(int, hmsysteme.get_pos()))
        # legacy / alternate API
        if hasattr(hmsysteme, "get_mouse"):
            mx, my, bstate, action = hmsysteme.get_mouse(None)
            if action:  # treat nonzero action as a hit trigger
                return True, (int(mx), int(my))
        if hasattr(hmsysteme, "last_hit"):
            pos = hmsysteme.last_hit()
            if pos:
                return True, (int(pos[0]), int(pos[1]))
    except Exception:
        pass
    return False, (0, 0)

# =========================== Board geometry ============================
R = BOARD_DIAMETER // 2
R_DOUBLE_OUTER = R
RING_WIDTH     = int(R * 0.047)      # ~8/170
R_DOUBLE_INNER = R_DOUBLE_OUTER - RING_WIDTH
R_TRIPLE_OUTER = int(R * 0.629)      # ~107/170
R_TRIPLE_INNER = R_TRIPLE_OUTER - RING_WIDTH
R_BULL_OUTER   = int(R * 0.094)      # ~16/170
R_BULL_INNER   = int(R * 0.037)      # ~6.3/170

# Colors
COL_BG         = (34, 34, 36)
COL_FACE       = (36, 36, 38)
COL_SINGLE_DK  = (40, 40, 40)
COL_SINGLE_LT  = (228, 219, 192)
COL_RING_RED   = (196, 35, 35)
COL_RING_GRN   = (18, 145, 80)
COL_BULL_RED   = (200, 38, 38)
COL_BULL_GRN   = (12, 140, 78)
COL_LINE       = (240, 240, 240)
COL_EDGE       = (20, 20, 20)
COL_TEXT       = (245, 240, 220)
COL_ACCENT     = (255, 210, 70)
COL_LABEL_BG   = (0, 0, 0, 170)

# Numbers ring order (20 at top, clockwise)
SECTOR_NUMBERS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]

# ====================== crisp annular drawing ==========================
def _annular_points(cx, cy, r_outer, r_inner, a0, a1, steps=96):
    pts = []
    for i in range(steps + 1):  # outer arc
        a = a0 + (a1 - a0) * (i / steps)
        pts.append((int(cx + r_outer * math.cos(a)), int(cy + r_outer * math.sin(a))))
    for i in range(steps, -1, -1):  # inner arc (reverse)
        a = a0 + (a1 - a0) * (i / steps)
        pts.append((int(cx + r_inner * math.cos(a)), int(cy + r_inner * math.sin(a))))
    return pts

def _fill_annular(surf, color, cx, cy, r_outer, r_inner, a0, a1, steps=96):
    pygame.draw.polygon(surf, color, _annular_points(cx, cy, r_outer, r_inner, a0, a1, steps), 0)

# ========================= Board rendering ============================
def make_board_surface(size, center):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    cx, cy = center
    FUDGE = 1

    # base + bevel
    pygame.draw.circle(surf, COL_FACE, center, R_DOUBLE_OUTER + 10)
    pygame.draw.circle(surf, COL_EDGE, center, R_DOUBLE_OUTER + 10, 10)

    # singles
    for i in range(20):
        a0 = math.radians(i * 18 - 9 - 90)
        a1 = math.radians((i + 1) * 18 - 9 - 90)
        col = COL_SINGLE_DK if i % 2 == 0 else COL_SINGLE_LT
        _fill_annular(surf, col, cx, cy, R_DOUBLE_INNER, R_TRIPLE_OUTER, a0, a1)
        _fill_annular(surf, col, cx, cy, R_TRIPLE_INNER, R_BULL_OUTER, a0, a1)

    # rings
    for i in range(20):
        a0 = math.radians(i * 18 - 9 - 90)
        a1 = math.radians((i + 1) * 18 - 9 - 90)
        col = COL_RING_RED if i % 2 == 0 else COL_RING_GRN
        _fill_annular(surf, col, cx, cy, R_TRIPLE_OUTER + FUDGE, R_TRIPLE_INNER - FUDGE, a0, a1)
        _fill_annular(surf, col, cx, cy, R_DOUBLE_OUTER,       R_DOUBLE_INNER - FUDGE, a0, a1)

    # bulls
    pygame.draw.circle(surf, COL_BULL_GRN, center, R_BULL_OUTER + FUDGE)
    pygame.draw.circle(surf, COL_BULL_RED, center, R_BULL_INNER)

    # rim
    pygame.draw.circle(surf, COL_LINE, center, R_DOUBLE_OUTER, 3)

    # numbers
    num_font = pygame.font.SysFont("Arial", 34, bold=True)
    for i, num in enumerate(SECTOR_NUMBERS):
        ang = math.radians(i * 18 - 90)
        r_text = R_DOUBLE_OUTER + 36
        x, y = cx + r_text * math.cos(ang), cy + r_text * math.sin(ang)
        pygame.draw.circle(surf, COL_EDGE, (int(x), int(y)), 24)
        pygame.draw.circle(surf, COL_LINE, (int(x), int(y)), 24, 3)
        text = num_font.render(str(num), True, COL_LINE)
        surf.blit(text, text.get_rect(center=(x, y)))

    return surf

# ============================== Scoring ===============================
def score_from_point(center, pos):
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

# ========================= Text helper ================================
def wrap_text(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if not cur or font.size(test)[0] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ====================== 180 animation (prebaked) ======================
def _rot(px, py, cx, cy, theta):
    s, c = math.sin(theta), math.cos(theta)
    px -= cx; py -= cy
    return px * c - py * s + cx, px * s + py * c + cy

def make_180_frames(width=900, height=520):
    n_frames = 24
    frames = []
    cx, ground = width // 2, int(height * 0.90)
    shoulder_y = int(height * 0.52)
    poster_w, poster_h = 420, 200
    y_poster = shoulder_y - 60
    amp = int(width * 0.12)
    rot_amp = math.radians(8)
    font_180 = pygame.font.SysFont("Arial", 140, bold=True)

    base = pygame.Surface((poster_w, poster_h), pygame.SRCALPHA)
    pygame.draw.rect(base, (250, 250, 250), (0, 0, poster_w, poster_h), border_radius=20)
    pygame.draw.rect(base, (20, 20, 22), (0, 0, poster_w, poster_h), width=6, border_radius=20)
    pygame.draw.rect(base, COL_RING_GRN, (0, 14, poster_w, 12), border_radius=6)
    pygame.draw.rect(base, COL_RING_RED, (0, poster_h-22, poster_w, 12), border_radius=6)
    txt = font_180.render("180", True, (20,20,22))
    base.blit(txt, txt.get_rect(center=(poster_w//2, poster_h//2)))

    for i in range(n_frames):
        t = i / (n_frames - 1)
        phase = math.sin(t * 2 * math.pi)
        px = cx + int(amp * phase)
        theta = rot_amp * phase
        frame = pygame.Surface((width, height), pygame.SRCALPHA)

        for x in range(0, width, 30):
            pygame.draw.circle(frame, (18,18,22), (x, ground+8), 18)
        for x in range(15, width, 36):
            pygame.draw.circle(frame, (12,12,15), (x, ground-8), 24)

        pygame.draw.rect(frame, (28,28,33), (cx-18, ground-120, 14, 120))
        pygame.draw.rect(frame, (28,28,33), (cx+4,  ground-120, 14, 120))
        pygame.draw.rect(frame, (36,36,42), (cx-50, shoulder_y+24, 100, 100), border_radius=12)
        pygame.draw.circle(frame, (220,195,160), (cx, shoulder_y), 24)

        rot = pygame.transform.rotate(base, math.degrees(theta))
        pr = rot.get_rect(center=(px, y_poster))
        frame.blit(rot, pr.topleft)

        tl = _rot(pr.centerx - poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        tr = _rot(pr.centerx + poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        pygame.draw.line(frame, (32,32,36), (cx-48, shoulder_y+36), tl, 10)
        pygame.draw.line(frame, (32,32,36), (cx+48, shoulder_y+36), tr, 10)

        frames.append(frame.convert_alpha())
    return frames

def make_180_frames_hq(width=900, height=520):
    # supersampled then downscaled – heavier but still okay when LOW_POWER=False
    n_frames = 36
    ss = 2
    W, H = width*ss, height*ss
    cx, ground = W // 2, int(H * 0.90)
    shoulder_y = int(H * 0.52)
    poster_w, poster_h = 820, 380
    y_poster = shoulder_y - 120
    amp = int(W * 0.15)
    rot_amp = math.radians(12)
    font_180 = pygame.font.SysFont("Arial", 300, bold=True)

    base = pygame.Surface((poster_w, poster_h), pygame.SRCALPHA)
    pygame.draw.rect(base, (250,250,250), (0,0,poster_w,poster_h), border_radius=28)
    pygame.draw.rect(base, (20,20,22), (0,0,poster_w,poster_h), width=10, border_radius=28)
    pygame.draw.rect(base, COL_RING_GRN, (0, 30, poster_w, 24), border_radius=12)
    pygame.draw.rect(base, COL_RING_RED, (0, poster_h-54, poster_w, 24), border_radius=12)
    txt = font_180.render("180", True, (20,20,22))
    base.blit(txt, txt.get_rect(center=(poster_w//2, poster_h//2)))

    frames = []
    for i in range(n_frames):
        t = i / (n_frames - 1)
        phase = math.sin(t * 2 * math.pi)
        px = cx + int(amp * phase)
        theta = rot_amp * phase
        frame = pygame.Surface((W, H), pygame.SRCALPHA)

        for x in range(0, W, 52):
            pygame.draw.circle(frame, (18,18,22), (x, ground+10), 40)
        for x in range(26, W, 64):
            pygame.draw.circle(frame, (12,12,15), (x, ground-10), 54)

        pygame.draw.rect(frame, (28,28,33), (cx-44, H-180, 36, 180))
        pygame.draw.rect(frame, (28,28,33), (cx+8,  H-180, 36, 180))
        pygame.draw.rect(frame, (36,36,42), (cx-90, shoulder_y+40, 180, 160), border_radius=20)
        pygame.draw.circle(frame, (220,195,160), (cx, shoulder_y), 52)

        rot = pygame.transform.rotate(base, math.degrees(theta))
        pr = rot.get_rect(center=(px, y_poster))
        frame.blit(rot, pr.topleft)

        tl = _rot(pr.centerx - poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        tr = _rot(pr.centerx + poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        pygame.draw.line(frame, (32,32,36), (cx-120, shoulder_y+80), tl, 28)
        pygame.draw.line(frame, (32,32,36), (cx+120, shoulder_y+80), tr, 28)

        frames.append(pygame.transform.smoothscale(frame, (width, height)).convert_alpha())
    return frames

# ============================ Game State ==============================
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 501
        self.throws_this_turn = 0

class Game:
    def __init__(self):
        pygame.init()
        flags = pygame.DOUBLEBUF
        if FULLSCREEN:
            flags |= pygame.FULLSCREEN
        depth = 16 if DEPTH_16BIT else 0
        pygame.display.set_caption("Darts — Pi-friendly")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), flags, depth)
        self.clock = pygame.time.Clock()

        # fonts
        self.font_big   = pygame.font.SysFont("Arial", 36, bold=True)
        self.font       = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20, bold=True)

        # board + layers (convert for faster blits)
        self.cx, self.cy = WINDOW_W // 2, WINDOW_H // 2
        self.board_surface = make_board_surface((WINDOW_W, WINDOW_H), (self.cx, self.cy)).convert_alpha()
        self.hits_surface  = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA).convert_alpha()
        self.overlay_surface = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA).convert_alpha()
        self.board_rect = self.board_surface.get_rect()

        # players
        self.players = [Player(f"Player {i}") for i in range(1, 5)]
        self.turn = 0
        self.max_throws = 3
        self.turn_labels = []   # list of (x, y, text)

        # 180 animation frames
        self.frames_180 = make_180_frames() if LOW_POWER else make_180_frames_hq()
        self.anim_on = False
        self.anim_idx = 0
        self.anim_timer = 0
        self.anim_loops = 0
        self.anim_loops_max = 2
        self.anim_interval = 60 if LOW_POWER else 38

        # caches
        self._cached_scores = None

        # first paint
        self.screen.fill(COL_BG)
        self.screen.blit(self.board_surface, (0, 0))
        self._draw_scores(full=True)
        pygame.display.flip()

    # board bounds including number circles
    def _board_bounds(self):
        NUM_RING_OFFSET = 36
        NUM_CIRCLE_OUTER = 24 + 3
        rb = R_DOUBLE_OUTER + NUM_RING_OFFSET + NUM_CIRCLE_OUTER
        return pygame.Rect(self.cx - rb, self.cy - rb, rb * 2, rb * 2)

    # UI drawing --------------------------------------------------------
    def _draw_scores(self, full=False):
        dirty = []
        bb = self._board_bounds()

        # left column
        LEFT_X = 24
        LEFT_RIGHT = bb.left - 12
        LEFT_W = max(0, LEFT_RIGHT - LEFT_X)

        # right panel
        PANEL_MARGIN = 12
        x0 = max(bb.right + PANEL_MARGIN, WINDOW_W - 320)
        PANEL_W = WINDOW_W - x0 - 10

        if full:
            if LEFT_W > 0:
                pygame.draw.rect(self.screen, COL_BG, pygame.Rect(LEFT_X - 8, 10, LEFT_W + 16, 80))
                dirty.append(pygame.Rect(LEFT_X - 8, 10, LEFT_W + 16, 80))
            if PANEL_W > 0:
                pygame.draw.rect(self.screen, COL_BG, pygame.Rect(x0, 10, PANEL_W, WINDOW_H - 20))
                dirty.append(pygame.Rect(x0, 10, PANEL_W, WINDOW_H - 20))

        # Header (left-of-board only; fit-to-band with two-line fallback; clipped so it never hits the board)
        if LEFT_W > 40:
            throws_left = self.max_throws - self.players[self.turn].throws_this_turn
            name = self.players[self.turn].name
            label_txt = f"{name} - throws left:"
            # UI band strictly to the left of the board
            band_w = max(0, bb.left - 8)
            avail_w = max(0, band_w - LEFT_X - 8)
            # Try big font on one line
            name_big = self.font_big.render(label_txt, True, COL_TEXT)
            num_big  = self.font_big.render(str(int(throws_left)), True, COL_TEXT)
            need_w_big = name_big.get_width() + 8 + num_big.get_width()
            use_two_lines = False
            if need_w_big <= avail_w:
                use_font = self.font_big
                line_h = self.font_big.get_height()
                band_h = line_h + 16
                ui_rect = pygame.Rect(0, 12, band_w, band_h)
                pygame.draw.rect(self.screen, COL_BG, ui_rect)
                prev_clip = self.screen.get_clip()
                self.screen.set_clip(ui_rect)
                x = LEFT_X
                y = ui_rect.y + (ui_rect.height - line_h)//2
                self.screen.blit(name_big, (x, y))
                self.screen.blit(num_big, (x + name_big.get_width() + 8, y))
                self.screen.set_clip(prev_clip)
                dirty.append(ui_rect)
            else:
                # Try small font on one line
                name_sm = self.font.render(label_txt, True, COL_TEXT)
                num_sm  = self.font.render(str(int(throws_left)), True, COL_TEXT)
                need_w_sm = name_sm.get_width() + 8 + num_sm.get_width()
                if need_w_sm <= avail_w:
                    line_h = self.font.get_height()
                    band_h = line_h + 16
                    ui_rect = pygame.Rect(0, 12, band_w, band_h)
                    pygame.draw.rect(self.screen, COL_BG, ui_rect)
                    prev_clip = self.screen.get_clip()
                    self.screen.set_clip(ui_rect)
                    x = LEFT_X
                    y = ui_rect.y + (ui_rect.height - line_h)//2
                    self.screen.blit(name_sm, (x, y))
                    self.screen.blit(num_sm, (x + name_sm.get_width() + 8, y))
                    self.screen.set_clip(prev_clip)
                    dirty.append(ui_rect)
                else:
                    # Two-line fallback with small font
                    name_line = self.font.render(name, True, COL_TEXT)
                    second_txt = f"throws left: {int(throws_left)}"
                    second_line = self.font.render(second_txt, True, COL_TEXT)
                    line_h = self.font.get_height()
                    band_h = line_h*2 + 16 + 4
                    ui_rect = pygame.Rect(0, 12, band_w, band_h)
                    pygame.draw.rect(self.screen, COL_BG, ui_rect)
                    prev_clip = self.screen.get_clip()
                    self.screen.set_clip(ui_rect)
                    x = LEFT_X
                    y1 = ui_rect.y + 8
                    y2 = y1 + line_h + 4
                    self.screen.blit(name_line, (x, y1))
                    self.screen.blit(second_line, (x, y2))
                    self.screen.set_clip(prev_clip)
                    dirty.append(ui_rect)

        # Scores panel
        scores_tuple = tuple(p.score for p in self.players)
        if full or scores_tuple != self._cached_scores:
            if PANEL_W > 40:
                title = self.font_big.render("SCORES", True, COL_TEXT)
                self.screen.blit(title, (x0, 24))
                VALUE_X = x0 + 150
                for i, pl in enumerate(self.players):
                    y = 70 + i * 36
                    line_rect = pygame.Rect(x0, y - 6, PANEL_W, 36)
                    pygame.draw.rect(self.screen, COL_BG, line_rect)
                    self.screen.blit(self.font.render(f"{pl.name}:", True, COL_TEXT), (x0, y))
                    col = COL_ACCENT if i == self.turn else COL_TEXT
                    self.screen.blit(self.font.render(str(pl.score), True, col), (VALUE_X, y))
                    dirty.append(line_rect)
            self._cached_scores = scores_tuple

        return dirty

    def _recompose_board_region(self):
        self.screen.blit(self.board_surface, (0, 0), area=self.board_rect)
        self.screen.blit(self.hits_surface, (0, 0), area=self.board_rect)
        self.screen.blit(self.overlay_surface, (0, 0), area=self.board_rect)
        return self.board_rect

    def _place_labels_overlay(self):
        self.overlay_surface.fill((0,0,0,0))
        pad = 6
        for (x, y, txt_str) in self.turn_labels:
            txt = self.font_small.render(txt_str, True, COL_TEXT)
            bw, bh = txt.get_width()+pad*2, txt.get_height()+pad*2
            bx0, by0 = x + 12, y - txt.get_height() - 8

            # clamp to circle so labels never cover the header area
            cx, cy = self.cx, self.cy
            half_diag = ((bw*0.5)**2 + (bh*0.5)**2) ** 0.5
            R_LIMIT = R_DOUBLE_OUTER - 8 - half_diag
            cxb, cyb = bx0 + bw*0.5, by0 + bh*0.5
            vx, vy = cxb - cx, cyb - cy
            dist = (vx*vx + vy*vy) ** 0.5
            if dist > R_LIMIT:
                if dist == 0: dist = 1.0
                scale = R_LIMIT / dist
                cxb = cx + vx * scale
                cyb = cy + vy * scale
            bx, by = int(cxb - bw*0.5), int(cyb - bh*0.5)

            bubble = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bubble.fill(COL_LABEL_BG)
            self.overlay_surface.blit(bubble.convert_alpha(), (bx, by))
            self.overlay_surface.blit(txt, (bx + pad, by + pad))

    # ============================ Gameplay =============================
    def next_player(self):
        self.players[self.turn].throws_this_turn = 0
        self.turn_labels.clear()
        self.hits_surface.fill((0,0,0,0))
        self.overlay_surface.fill((0,0,0,0))
        self.turn = (self.turn + 1) % len(self.players)
        dirty = [self._recompose_board_region()]
        dirty += self._draw_scores(full=True)
        pygame.display.update(dirty)

    def handle_throw(self, pos):
        x = max(0, min(WINDOW_W-1, int(pos[0])))
        y = max(0, min(WINDOW_H-1, int(pos[1])))

        p = self.players[self.turn]
        if p.throws_this_turn >= self.max_throws:
            return

        score, mult, sect, label = score_from_point((self.cx, self.cy), (x, y))

        if p.score - score >= 0:
            p.score -= score
            p.throws_this_turn += 1

            # dot
            pygame.draw.circle(self.hits_surface, COL_ACCENT, (x, y), 6)
            # label for THIS throw (keep all 3)
            self.turn_labels.append((x, y, f"{score} ({label})"))
            self._place_labels_overlay()

            # recompose entire board area so dots + all labels appear immediately
            dirty = [self._recompose_board_region()]
            dirty += self._draw_scores(full=False)
            pygame.display.update(dirty)

            # 180 celebration
            if p.throws_this_turn == 3:
                turn_sum = sum(int(lbl.split()[0]) for (_,_,lbl) in self.turn_labels if lbl.split()[0].isdigit())
                if turn_sum == 180:
                    self.trigger_180_animation()

        if p.score == 0 or p.throws_this_turn >= self.max_throws:
            self.next_player()

    # ======================== Animation control =======================
    def trigger_180_animation(self):
        self.anim_on = True
        self.anim_idx = 0
        self.anim_timer = pygame.time.get_ticks()
        self.anim_loops = 0

    def step_animation(self):
        if not self.anim_on:
            return False
        now = pygame.time.get_ticks()
        if now - self.anim_timer >= self.anim_interval:
            self.anim_timer = now
            self.anim_idx += 1
            if self.anim_idx >= len(self.frames_180):
                self.anim_idx = 0
                self.anim_loops += 1
                if self.anim_loops >= self.anim_loops_max:
                    self.anim_on = False
        return self.anim_on

    def draw_animation_frame(self):
        dim = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA).convert_alpha()
        dim.fill((0, 0, 0, 160))
        self.screen.blit(self.board_surface, (0, 0))
        self.screen.blit(self.hits_surface, (0, 0))
        self.screen.blit(dim, (0, 0))

        frame = self.frames_180[self.anim_idx]
        rect = frame.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 40))
        self.screen.blit(frame, rect.topleft)
        pygame.display.flip()

    # ============================= Main loop ==========================
    def run(self):
        running = True
        while running:
            prev_anim = self.anim_on

            # poll hardware sensor (lightweight)
            hit, pos = hw_poll()
            if hit and not self.anim_on:
                self.handle_throw(pos)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    self.players[self.turn].score = 501
                    self.players[self.turn].throws_this_turn = 0
                    self.turn_labels.clear()
                    self.hits_surface.fill((0,0,0,0))
                    self.overlay_surface.fill((0,0,0,0))
                    dirty = [self._recompose_board_region()]
                    dirty += self._draw_scores(full=True)
                    pygame.display.update(dirty)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_n:
                    self.next_player()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not self.anim_on:
                    self.handle_throw(e.pos)

            if self.step_animation():
                self.draw_animation_frame()
                self.clock.tick(FPS_ANIM)
                continue
            elif prev_anim and not self.anim_on:
                dirty = [self._recompose_board_region()]
                dirty += self._draw_scores(full=True)
                pygame.display.update(dirty)

            self.clock.tick(FPS_IDLE)

        pygame.quit()

def main():
    Game().run()

if __name__ == "__main__":
    main()
