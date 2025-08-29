#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Darts – sharp board, Pi Zero 2 friendly, current-player-only dots,
hardware hit support (hmsysteme), and non-overlapping UI.
Includes a lightweight 180 animation (LOW_POWER) and a nicer HQ version.
"""

import math
import random
import pygame

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
LOW_POWER = True           # set False on desktop for fancier 180 animation
WINDOW_W, WINDOW_H = 1280, 900
BOARD_DIAMETER = 720
FPS_IDLE = 30
FPS_ANIM = 50

# -------------------------------------------------------------------
# Optional hardware module (hmsysteme) for real hit detection
# -------------------------------------------------------------------
try:
    import hmsysteme  # must expose: hit_detected() -> bool, get_pos() -> (x,y)
    HAVE_HW = hasattr(hmsysteme, "hit_detected") and hasattr(hmsysteme, "get_pos")
except Exception:       # safe fallback for development
    hmsysteme = None
    HAVE_HW = False

# -------------------------------------------------------------------
# Board geometry
# -------------------------------------------------------------------
R = BOARD_DIAMETER // 2
R_DOUBLE_OUTER = R
RING_WIDTH     = int(R * 0.047)      # ~8/170 of outer
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

SECTOR_NUMBERS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]


# ---------- crisp annular-sector (no AA) ----------
def _annular_points(cx, cy, r_outer, r_inner, a0, a1, steps=96):
    """Polygon points for a filled annular sector; curved edges via many short chords."""
    pts = []
    for i in range(steps + 1):                     # outer arc a0 -> a1
        a = a0 + (a1 - a0) * (i / steps)
        pts.append((int(cx + r_outer * math.cos(a)), int(cy + r_outer * math.sin(a))))
    for i in range(steps, -1, -1):                 # inner arc a1 -> a0
        a = a0 + (a1 - a0) * (i / steps)
        pts.append((int(cx + r_inner * math.cos(a)), int(cy + r_inner * math.sin(a))))
    return pts

def _fill_annular(surf, color, cx, cy, r_outer, r_inner, a0, a1, steps=96):
    pygame.draw.polygon(surf, color, _annular_points(cx, cy, r_outer, r_inner, a0, a1, steps), 0)


# ---------------- Board drawing (sharp, static) ----------------
def make_board_surface(size, center):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    cx, cy = center
    FUDGE = 1

    # Base & outer bevel
    pygame.draw.circle(surface, COL_FACE, center, R_DOUBLE_OUTER + 10)
    pygame.draw.circle(surface, COL_EDGE, center, R_DOUBLE_OUTER + 10, 10)

    # Singles
    for i in range(20):
        a0 = math.radians(i * 18 - 9 - 90)
        a1 = math.radians((i + 1) * 18 - 9 - 90)
        col = COL_SINGLE_DK if i % 2 == 0 else COL_SINGLE_LT
        _fill_annular(surface, col, cx, cy, R_DOUBLE_INNER, R_TRIPLE_OUTER, a0, a1)
        _fill_annular(surface, col, cx, cy, R_TRIPLE_INNER, R_BULL_OUTER, a0, a1)

    # Rings
    for i in range(20):
        a0 = math.radians(i * 18 - 9 - 90)
        a1 = math.radians((i + 1) * 18 - 9 - 90)
        col = COL_RING_RED if i % 2 == 0 else COL_RING_GRN
        _fill_annular(surface, col, cx, cy, R_TRIPLE_OUTER + FUDGE, R_TRIPLE_INNER - FUDGE, a0, a1)
        _fill_annular(surface, col, cx, cy, R_DOUBLE_OUTER,       R_DOUBLE_INNER - FUDGE, a0, a1)

    # Bulls
    pygame.draw.circle(surface, COL_BULL_GRN, center, R_BULL_OUTER + FUDGE)
    pygame.draw.circle(surface, COL_BULL_RED, center, R_BULL_INNER)

    # Rim
    pygame.draw.circle(surface, COL_LINE, center, R_DOUBLE_OUTER, 3)

    # Numbers
    num_font = pygame.font.SysFont("Arial", 34, bold=True)
    for i, num in enumerate(SECTOR_NUMBERS):
        ang = math.radians(i * 18 - 90)
        r_text = R_DOUBLE_OUTER + 36
        x, y = cx + r_text * math.cos(ang), cy + r_text * math.sin(ang)
        pygame.draw.circle(surface, COL_EDGE, (int(x), int(y)), 24)
        pygame.draw.circle(surface, COL_LINE, (int(x), int(y)), 24, 3)
        text = num_font.render(str(num), True, COL_LINE)
        surface.blit(text, text.get_rect(center=(x, y)))

    return surface


# ---------------- Scoring ----------------
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


# ---------------- Text helpers ----------------
def render_text_outline(text, font, color, outline_color=(0,0,0), outline_px=3):
    base = font.render(text, True, color)
    w, h = base.get_size()
    surf = pygame.Surface((w + 2*outline_px, h + 2*outline_px), pygame.SRCALPHA)
    for dx in range(-outline_px, outline_px+1):
        for dy in range(-outline_px, outline_px+1):
            if dx*dx + dy*dy <= outline_px*outline_px:
                surf.blit(font.render(text, True, outline_color), (dx + outline_px, dy + outline_px))
    surf.blit(base, (outline_px, outline_px))
    return surf

def wrap_text(text, font, max_w):
    """Simple word-wrap; returns list of lines that fit within max_w."""
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


# ---------------- 180 animation (two quality levels) ----------------
def _rot(px, py, cx, cy, theta):
    s, c = math.sin(theta), math.cos(theta)
    px -= cx; py -= cy
    return px * c - py * s + cx, px * s + py * c + cy

def make_180_frames(width=900, height=520):
    """Simplified frames for LOW_POWER mode (fewer frames, no supersampling)."""
    n_frames = 24
    frames = []
    cx, ground = width // 2, int(height * 0.90)
    shoulder_y = int(height * 0.52)
    poster_w, poster_h = 420, 200
    y_poster = shoulder_y - 60
    amp = int(width * 0.12)
    rot_amp = math.radians(8)
    font_180 = pygame.font.SysFont("Arial", 140, bold=True)

    # build poster
    base = pygame.Surface((poster_w, poster_h), pygame.SRCALPHA)
    pygame.draw.rect(base, (250, 250, 250), (0, 0, poster_w, poster_h), border_radius=20)
    pygame.draw.rect(base, (20, 20, 22), (0, 0, poster_w, poster_h), width=6, border_radius=20)
    pygame.draw.rect(base, COL_RING_GRN, (0, 14, poster_w, 12), border_radius=6)
    pygame.draw.rect(base, COL_RING_RED, (0, poster_h-22, poster_w, 12), border_radius=6)
    txt = font_180.render("180", True, (20, 20, 22))
    base.blit(txt, txt.get_rect(center=(poster_w//2, poster_h//2)))

    for i in range(n_frames):
        t = i / (n_frames - 1)
        phase = math.sin(t * 2 * math.pi)
        px = cx + int(amp * phase)
        theta = rot_amp * phase
        frame = pygame.Surface((width, height), pygame.SRCALPHA)

        # simple crowd
        for x in range(0, width, 30):
            pygame.draw.circle(frame, (18,18,22), (x, ground+8), 18)
        for x in range(15, width, 36):
            pygame.draw.circle(frame, (12,12,15), (x, ground-8), 24)

        # person
        pygame.draw.rect(frame, (28,28,33), (cx-18, ground-120, 14, 120))
        pygame.draw.rect(frame, (28,28,33), (cx+4,  ground-120, 14, 120))
        pygame.draw.rect(frame, (36,36,42), (cx-50, shoulder_y+24, 100, 100), border_radius=12)
        pygame.draw.circle(frame, (220,195,160), (cx, shoulder_y), 24)

        # poster
        rot = pygame.transform.rotate(base, math.degrees(theta))
        pr = rot.get_rect(center=(px, y_poster))
        frame.blit(rot, pr.topleft)

        # arms
        tl = _rot(pr.centerx - poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        tr = _rot(pr.centerx + poster_w/2, pr.centery - poster_h/2, pr.centerx, pr.centery, theta)
        pygame.draw.line(frame, (32,32,36), (cx-48, shoulder_y+36), tl, 10)
        pygame.draw.line(frame, (32,32,36), (cx+48, shoulder_y+36), tr, 10)

        frames.append(frame)
    return frames

def make_180_frames_hq(width=900, height=520):
    """Higher-quality frames (still Pi-friendly, generated once)."""
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

        # crowd
        for x in range(0, W, 52):
            pygame.draw.circle(frame, (18,18,22), (x, ground+10), 40)
        for x in range(26, W, 64):
            pygame.draw.circle(frame, (12,12,15), (x, ground-10), 54)

        # person
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

        frames.append(pygame.transform.smoothscale(frame, (width, height)))
    return frames


# ---------------- Simple 501 scaffold ----------------
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 501
        self.throws_this_turn = 0


class Game:
    def __init__(self):
        pygame.init()
        flags = pygame.DOUBLEBUF
        pygame.display.set_caption("Darts — Pi-friendly")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), flags)
        self.clock = pygame.time.Clock()

        # Board + layers
        self.cx, self.cy = WINDOW_W // 2, WINDOW_H // 2
        self.board_surface = make_board_surface((WINDOW_W, WINDOW_H), (self.cx, self.cy))
        self.hits_surface = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)  # small additions
        self.overlay_surface = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)  # ephemeral labels
        self.board_rect = self.board_surface.get_rect()

        # Players
        self.players = [Player(f"Player {i}") for i in range(1, 5)]
        self.turn = 0
        self.max_throws = 3
        self.turn_points = []
        self.turn_hits = []      # (pos, score, mult, label)

        # Fonts / banner
        self.font_big   = pygame.font.SysFont("Arial", 36, bold=True)
        self.font       = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20, bold=True)
        self.banner_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.banner_surf = render_text_outline("ONE HUNDRED AND EIGHTY!",
                                               self.banner_font, (255,255,255), (0,0,0), 4)

        # Animation frames (once)
        self.frames_180 = make_180_frames() if LOW_POWER else make_180_frames_hq()
        self.anim_on = False
        self.anim_idx = 0
        self.anim_timer = 0
        self.anim_loops = 0
        self.anim_loops_max = 2
        self.anim_interval = 60 if LOW_POWER else 38

        # HUD cache (for partial redraw)
        self._cached_scores = None
        self._cached_player = None
        self._cached_throws = None

        # First paint (static) and flip
        self.screen.fill(COL_BG)
        self.screen.blit(self.board_surface, (0, 0))
        self._draw_scores(full=True)
        pygame.display.flip()

    # ---------- Board bounds ----------
    def _board_bounds(self):
        """Outer pixel bounds of the board including number circles."""
        NUM_RING_OFFSET = 36    # numbers distance from double-outer
        NUM_CIRCLE_OUTER = 24 + 3  # circle radius + outline
        rb = R_DOUBLE_OUTER + NUM_RING_OFFSET + NUM_CIRCLE_OUTER
        return pygame.Rect(self.cx - rb, self.cy - rb, rb * 2, rb * 2)

    # ---------- UI helpers (only update when changed) ----------
    def _draw_scores(self, full=False):
        dirty = []

        bb = self._board_bounds()

        # Left column area (for header + footer)
        LEFT_X = 24
        LEFT_RIGHT = bb.left - 12               # stop before the board
        LEFT_W = max(0, LEFT_RIGHT - LEFT_X)

        # Right panel (scores) placed strictly to the right of the board
        PANEL_MARGIN = 12
        x0 = max(bb.right + PANEL_MARGIN, WINDOW_W - 320)   # safe + default
        PANEL_W = WINDOW_W - x0 - 10

        if full:
            # Clear only the UI areas
            left_clear = pygame.Rect(LEFT_X - 8, 10, max(0, LEFT_W + 16), 140)  # header zone
            right_clear = pygame.Rect(x0, 10, max(0, PANEL_W), WINDOW_H - 20)   # score panel
            if left_clear.width > 0:
                pygame.draw.rect(self.screen, COL_BG, left_clear)
                dirty.append(left_clear)
            if right_clear.width > 0:
                pygame.draw.rect(self.screen, COL_BG, right_clear)
                dirty.append(right_clear)

        # ----- Header (never over board) -----
        throws_left = self.max_throws - self.players[self.turn].throws_this_turn
        need_full_header = (full or
                            self._cached_player != self.turn or
                            self._cached_throws != throws_left)

        if need_full_header and LEFT_W > 40:
            header_text = f"{self.players[self.turn].name} — throws left: {throws_left}"
            hdr = self.font_big.render(header_text, True, COL_TEXT)
            header_rect = pygame.Rect(LEFT_X, 12, LEFT_W, hdr.get_height() + 20)
            pygame.draw.rect(self.screen, COL_BG, header_rect)

            if hdr.get_width() <= LEFT_W:
                self.screen.blit(hdr, (LEFT_X, 24))
            else:
                name_s = self.font_big.render(self.players[self.turn].name, True, COL_TEXT)
                tl_s   = self.font_big.render(f"throws left: {throws_left}", True, COL_TEXT)
                self.screen.blit(name_s, (LEFT_X, 16))
                self.screen.blit(tl_s,   (LEFT_X, 16 + name_s.get_height() + 6))

            dirty.append(header_rect)
            self._cached_player = self.turn
            self._cached_throws = throws_left

        # ----- Scores panel (right side) -----
        scores_tuple = tuple(p.score for p in self.players)
        if full or scores_tuple != self._cached_scores:
            if PANEL_W > 40:
                title = self.font_big.render("SCORES", True, COL_TEXT)
                self.screen.blit(title, (x0, 24))

                VALUE_X = x0 + 150  # move numbers closer to labels
                for i, pl in enumerate(self.players):
                    y = 70 + i * 36
                    line_rect = pygame.Rect(x0, y - 6, PANEL_W, 36)
                    pygame.draw.rect(self.screen, COL_BG, line_rect)
                    label = self.font.render(f"{pl.name}:", True, COL_TEXT)
                    val   = self.font.render(str(pl.score), True, COL_ACCENT if i == self.turn else COL_TEXT)
                    self.screen.blit(label, (x0, y))
                    self.screen.blit(val,   (VALUE_X, y))
                    dirty.append(line_rect)

            self._cached_scores = scores_tuple

        # ----- Footer (in the left column, not across board) -----
        if full and LEFT_W > 60:
            footer_msg = "Click board or use sensor to throw • R = reset player • N = next player • Esc = quit"
            lines = wrap_text(footer_msg, self.font, LEFT_W)
            y = WINDOW_H - 10
            line_h = self.font.get_height() + 4
            foot_dirty = []
            for s in reversed(lines):
                y -= line_h
                r = pygame.Rect(LEFT_X, y, LEFT_W, line_h)
                pygame.draw.rect(self.screen, COL_BG, r)
                self.screen.blit(self.font.render(s, True, COL_TEXT), (LEFT_X, y))
                foot_dirty.append(r)
            dirty += foot_dirty

        return dirty

    def _recompose_board_region(self):
        """Re-blit board + current hits to the board rect (once), return rect."""
        self.screen.blit(self.board_surface, (0, 0))
        self.screen.blit(self.hits_surface, (0, 0))
        self.screen.blit(self.overlay_surface, (0, 0))
        return self.board_rect

    # ---------- Gameplay ----------
    def next_player(self):
        self.players[self.turn].throws_this_turn = 0
        self.turn_points.clear()
        self.turn_hits.clear()
        self.hits_surface.fill((0,0,0,0))  # clear dots layer
        self.turn = (self.turn + 1) % len(self.players)
        self.overlay_surface.fill((0,0,0,0))
        dirty = [self._recompose_board_region()]
        dirty += self._draw_scores(full=True)
        pygame.display.update(dirty)

    def handle_throw(self, pos):
        # clamp to screen
        x = max(0, min(WINDOW_W-1, int(pos[0])))
        y = max(0, min(WINDOW_H-1, int(pos[1])))

        p = self.players[self.turn]
        if p.throws_this_turn >= self.max_throws:
            return

        score, mult, sect, label = score_from_point((self.cx, self.cy), (x, y))

        # basic 501: ignore negative
        if p.score - score >= 0:
            p.score -= score
            p.throws_this_turn += 1
            self.turn_hits.append(((x, y), score, mult, label))

            # draw the small dart dot on the hits layer
            pygame.draw.circle(self.hits_surface, COL_ACCENT, (x, y), 6)

            # recomposite board area and update only that rectangle
            dirty = [self._recompose_board_region()]

            # last-shot bubble near the dart (rendered on overlay surface and clamped to board circle)
            txt = self.font_small.render(f"{score} ({label})", True, COL_TEXT)
            # draw last-shot bubble on the overlay surface, not directly on screen, so it's easy to clear
            self.overlay_surface.fill((0,0,0,0))

            pad = 6
            bubble = pygame.Surface((txt.get_width()+pad*2, txt.get_height()+pad*2), pygame.SRCALPHA)
            bubble.fill(COL_LABEL_BG)

            # Proposed bubble center near the dart
            bx0 = x + 12
            by0 = y - txt.get_height() - 8
            bw, bh = bubble.get_width(), bubble.get_height()
            cx, cy = self.cx, self.cy

            # Clamp bubble center to stay fully inside a circle (double outer - margin)
            # Use half-diagonal of the bubble as safety margin.
            half_diag = ( (bw*0.5)**2 + (bh*0.5)**2 ) ** 0.5
            R_LIMIT = R_DOUBLE_OUTER - 8 - half_diag

            cxb, cyb = bx0 + bw*0.5, by0 + bh*0.5
            vx, vy = cxb - cx, cyb - cy
            dist = (vx*vx + vy*vy) ** 0.5
            if dist > R_LIMIT:
                if dist == 0:
                    dist = 1.0
                scale = R_LIMIT / dist
                cxb = cx + vx * scale
                cyb = cy + vy * scale

            # Final top-left
            bx = int(cxb - bw*0.5)
            by = int(cyb - bh*0.5)

            self.overlay_surface.blit(bubble, (bx, by))
            self.overlay_surface.blit(txt, (bx + pad, by + pad))
            dirty.append(pygame.Rect(bx, by, bw, bh))


            # scores / header
            dirty += self._draw_scores(full=False)
            pygame.display.update(dirty)

            # 180 celebration?
            self.turn_points.append(score)
            if len(self.turn_points) == 3 and sum(self.turn_points) == 180:
                self.trigger_180_animation()

        if p.score == 0 or p.throws_this_turn >= self.max_throws:
            self.next_player()

    # ---------- Animation ----------
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
        # dim background
        dim = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        self.screen.blit(self.board_surface, (0, 0))
        self.screen.blit(self.hits_surface, (0, 0))
        self.screen.blit(dim, (0, 0))

        frame = self.frames_180[self.anim_idx]
        rect = frame.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 40))
        self.screen.blit(frame, rect.topleft)


        pygame.display.flip()

    # ---------- Main loop ----------
    def run(self):
        running = True

        while running:
            prev_anim = self.anim_on
            # Hardware sensor hit?
            if HAVE_HW and not self.anim_on and hmsysteme.hit_detected():
                hx, hy = hmsysteme.get_pos()
                self.handle_throw((hx, hy))

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    # reset current player
                    self.players[self.turn].score = 501
                    self.players[self.turn].throws_this_turn = 0
                    self.turn_hits.clear()
                    self.turn_points.clear()
                    self.hits_surface.fill((0,0,0,0))
                    self.overlay_surface.fill((0,0,0,0))
                    dirty = [self._recompose_board_region()]
                    dirty += self._draw_scores(full=True)
                    pygame.display.update(dirty)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_n:
                    self.next_player()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not self.anim_on:
                    self.handle_throw(e.pos)

            # Animation step (if active, full-frame but short-lived)
            if self.step_animation():
                self.draw_animation_frame()
                self.clock.tick(FPS_ANIM)
                continue
            elif prev_anim and not self.anim_on:
                dirty = [self._recompose_board_region()]
                dirty += self._draw_scores(full=True)
                pygame.display.update(dirty)

            # Idle: nothing to update; just sleep a little
            self.clock.tick(FPS_IDLE)

        pygame.quit()


# --------- ENTRY POINT (for external launcher) ----------
def main():
    Game().run()

if __name__ == "__main__":
    main()
