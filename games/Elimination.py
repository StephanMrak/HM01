# Elimination_levels.py — 1366x768 fix • HM+Maus • KO-Turnier
# Level 1: Baum + Früchte (Explosion + zusätzliches Herunterfallen)
# Level 2: Wilder Westen (8 Gangsta, rote Explosion + Death gleichzeitig, Balkon-Overlay PNG)
# Reihenfolge: WEST zuerst (Debug), dann BAUM

import os, random, math, pygame

# ---------------- optionale hmsysteme-Wrapper ----------------
try:
    import hmsysteme

    HAS_HM = True
except Exception:
    HAS_HM = False


def hm_names():
    if HAS_HM and hasattr(hmsysteme, "get_playernames"):
        try:
            return hmsysteme.get_playernames()
        except Exception:
            pass
    return []


def hm_game_active():
    if HAS_HM and hasattr(hmsysteme, "game_isactive"):
        try:
            return hmsysteme.game_isactive()
        except Exception:
            pass
    return True


def hm_hit_detected():
    return HAS_HM and hasattr(hmsysteme, "hit_detected") and hmsysteme.hit_detected()


def hm_get_pos():
    if HAS_HM and hasattr(hmsysteme, "get_pos"):
        try:
            return hmsysteme.get_pos()
        except Exception:
            return None
    return None


def hm_screenshot(screen):
    if HAS_HM and hasattr(hmsysteme, "take_screenshot"):
        try:
            hmsysteme.take_screenshot(screen)
        except Exception:
            pass


def hm_buttons(labels):
    if HAS_HM and hasattr(hmsysteme, "put_button_names"):
        try:
            hmsysteme.put_button_names(labels)
        except Exception:
            pass


# ---------------- Konfiguration ----------------
WIDTH, HEIGHT = 1366, 768
FPS_LIMIT = 30
CROSS_FLASH_MS = 120

# Explosion / Effekt
EXP_DURATION = 0.9
GRAVITY = 1300.0
MAX_SHARDS = 32
SPARK_COUNT = 70
FLASH_MS = 110
SHAKE_MS = 220
SHAKE_AMPL = 12
SHOCK_MS = 280

RIGHT_INSET = 90
ASSET_ROOT = os.path.dirname(os.path.realpath(__file__))
WEST_DEATH_FPS = 9


# -------- Shake-Helper --------
def shake_offset(ms_since_start: int) -> tuple[int, int]:
    if ms_since_start >= SHAKE_MS: return (0, 0)
    k = 1.0 - (ms_since_start / SHAKE_MS)
    amp = max(0, int(SHAKE_AMPL * k))
    return (random.randint(-amp, amp), random.randint(-amp, amp))


# ---------------- Asset-Loader ----------------
def try_load_img(path):
    if not path: return None
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"[Asset-Warnung] {path} -> {e}")
        return None


def load_img(path, size=None, placeholder=None):
    surf = try_load_img(path)
    if surf is None:
        if placeholder is None:
            surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(surf, (30, 200, 60), (40, 40), 36)
            pygame.draw.circle(surf, (255, 255, 255), (40, 40), 36, 2)
        else:
            surf = placeholder
    if size:
        surf = pygame.transform.smoothscale(surf, size)
    return surf


def render_outlined(text, font, color, outline=(0, 0, 0), thick=1):
    base = font.render(text, True, color)
    outl = font.render(text, True, outline)
    w, h = base.get_width() + 2 * thick, base.get_height() + 2 * thick
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in (-thick, 0, thick):
        for dy in (-thick, 0, thick):
            if dx == 0 and dy == 0: continue
            surf.blit(outl, (dx + thick, dy + thick))
    surf.blit(base, (thick, thick))
    return surf


# ---------------- Ziele/Level ----------------
class Target:
    __slots__ = ("name", "surf", "mask", "x", "y", "done", "death_frames")

    def __init__(self, name, surf, pos, death_frames=None):
        self.name = name
        self.surf = surf
        self.mask = pygame.mask.from_surface(surf)
        self.x, self.y = pos
        self.done = False
        self.death_frames = death_frames

    def reset(self):
        self.done = False

    def draw(self, screen, offset=(0, 0)):
        if not self.done:
            ox, oy = int(offset[0]), int(offset[1])
            screen.blit(self.surf, (int(self.x) + ox, int(self.y) + oy))


class OverlayImage:
    """PNG mit Alphakanal, das über der Szene liegt (z.B. Geländer)."""
    __slots__ = ("surf", "pos")

    def __init__(self, surf, pos):
        self.surf = surf
        self.pos = pos


class Level:
    def __init__(self, name, bg_rel_path):
        self.name = name
        self.bg_path = os.path.join(ASSET_ROOT, bg_rel_path)
        self.bg = None
        self.targets = []
        self.overlays = []  # Liste OverlayImage

    def load_bg(self):
        raw = try_load_img(self.bg_path)
        if raw is None:
            print(f"[Asset] BG fehlt -> schwarz: {self.bg_path}")
            self.bg = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
            self.bg.fill((0, 0, 0, 255))
        else:
            self.bg = pygame.transform.smoothscale(raw, (WIDTH, HEIGHT))

    def all_down(self):
        return all(t.done for t in self.targets)

    def draw(self, screen, offset=(0, 0)):
        ox, oy = int(offset[0]), int(offset[1])
        screen.blit(self.bg, (ox, oy))
        for t in self.targets:
            t.draw(screen, (ox, oy))

    def draw_overlays(self, screen, offset=(0, 0)):
        ox, oy = int(offset[0]), int(offset[1])
        for ov in self.overlays:
            screen.blit(ov.surf, (ov.pos[0] + ox, ov.pos[1] + oy))
    def reset_targets(self):
        for t in self.targets:
            t.reset()


# ---------- Level 1: Früchte ----------
FRUITS_DEF = [
    ("Jackfruit", "pics/Elimination/Groß/Jackfruitx.png", (110, 159), (350, 410)),
    ("Stinkfrucht", "pics/Elimination/Groß/Stinkfruchtx.png", (110, 167), (550, 470)),
    ("Ananas", "pics/Elimination/Groß/Ananas.png", (110, 192), (750, 430)),
    ("Sauersack", "pics/Elimination/Groß/Sauersackx.png", (110, 177), (950, 410)),
    ("Kiwi", "pics/Elimination/Mittel/Kiwi.png", (80, 73), (510, 310)),
    ("Birne", "pics/Elimination/Mittel/Birne.png", (70, 86), (660, 310)),
    ("Bananen", "pics/Elimination/Mittel/Bananen.png", (110, 99), (360, 250)),
    ("Apfel", "pics/Elimination/Mittel/Apfel.png", (70, 87), (940, 260)),
    ("Orange", "pics/Elimination/Mittel/Orange.png", (85, 73), (790, 310)),
    ("Himbeere", "pics/Elimination/Klein/Himbeere.png", (40, 50), (750, 150)),
    ("Kirsche", "pics/Elimination/Klein/Kirsche.png", (50, 51), (630, 150)),
    ("Brombeere", "pics/Elimination/Klein/Brombeere.png", (60, 77), (850, 170)),
    ("Erdbeere", "pics/Elimination/Klein/Erdbeere.png", (60, 87), (510, 160)),
]


def build_level1():
    L = Level("Baum", "pics/Elimination/Baum.png")
    L.load_bg()
    L.targets = []
    for name, rel, size, pos in FRUITS_DEF:
        surf = load_img(os.path.join(ASSET_ROOT, rel), size)
        L.targets.append(Target(name, surf, pos))
    return L


# ---------- Level 2: Wilder Westen ----------
WEST_BG_REL = "pics/Elimination/West/Background.png"
GANGSTA_DIR_REL = "pics/Elimination/West/Gangsta"

# Deine neuen Positionen/Skalierungen:
GANGSTA_SPOTS = [
    (145, 255, 2.3),   # 1: links Balkon oben (hinter Geländer)
    (70,  455, 2.5),   # 2: links unten Eingang
    (350, 510, 1.3),   # 3: mittig links
    (550, 550, 0.55),  # 4: weit hinten
    (770, 500, 1.3),   # 5: mittig rechts
    (1148,200, 2.5),   # 6: rechts Balkon oben
    (1050,450, 2.5),   # 7: rechts unten Eingang
    (560, 450, 3.30),  # 8: ganz vorne Straße
]

# Overlay PNGs (mit Alpha) – Position relativ zum 1366x768-BG
OVERLAY_LEFT_PATH = os.path.join(ASSET_ROOT, "pics/Elimination/West/Overlays/left_balcony.png")
OVERLAY_LEFT_POS = (0, 0)


def load_gangsta_sequence_raw():
    idle = load_img(os.path.join(ASSET_ROOT, GANGSTA_DIR_REL, "1.png"))
    deaths = []
    for i in range(2, 20):
        p = os.path.join(ASSET_ROOT, GANGSTA_DIR_REL, f"{i}.png")
        if os.path.exists(p):
            deaths.append(load_img(p))
        else:
            break
    return idle, deaths


def scale_sequence(idle, deaths, scale):
    if scale == 1.0: return idle, list(deaths)
    return (pygame.transform.rotozoom(idle, 0, scale),
            [pygame.transform.rotozoom(f, 0, scale) for f in deaths])


def build_level2():
    L = Level("Wilder Westen", WEST_BG_REL)
    L.load_bg()
    ov = try_load_img(OVERLAY_LEFT_PATH)
    if ov:
        L.overlays.append(OverlayImage(ov, OVERLAY_LEFT_POS))
    else:
        print("[Overlay-Hinweis] left_balcony.png nicht gefunden – Geländer-Überdeckung ist deaktiviert.")
    idle_raw, deaths_raw = load_gangsta_sequence_raw()
    targets = []
    for i, (x, y, s) in enumerate(GANGSTA_SPOTS, 1):
        idle, deaths = scale_sequence(idle_raw, deaths_raw, s)
        targets.append(Target(f"Gangsta {i}", idle, (x, y), death_frames=deaths))
    L.targets = targets
    return L


# ---------------- Explosion (allgemein) ----------------
class Shard:
    __slots__ = ("surf", "x", "y", "vx", "vy", "angle", "omega", "alpha")

    def __init__(self, surf, x, y, vx, vy, angle, omega):
        self.surf = surf;
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy;
        self.angle = angle;
        self.omega = omega
        self.alpha = 255


class Spark:
    __slots__ = ("x", "y", "vx", "vy", "life", "r", "color")

    def __init__(self, x, y, vx, vy, life, r, color):
        self.x, self.y = x, y;
        self.vx, self.vy = vx, vy;
        self.life = life;
        self.r = r;
        self.color = color


def make_explosion_from_surface(surf, world_x, world_y, override_color=None):
    shards = []
    fw, fh = surf.get_width(), surf.get_height()
    cx, cy = world_x + fw / 2, world_y + fh / 2

    tile = max(10, min(20, min(fw, fh) // 6))
    cols = max(1, fw // tile);
    rows = max(1, fh // tile)
    candidates = []
    for cyi in range(rows):
        for cxi in range(cols):
            rx, ry = cxi * tile, cyi * tile
            rect = pygame.Rect(rx, ry, tile, tile)
            sub = surf.subsurface(rect)
            br = sub.get_bounding_rect(min_alpha=10)
            if br.width == 0 or br.height == 0: continue
            piece = sub.subsurface(br).copy()
            px = world_x + rx + br.x;
            py = world_y + ry + br.y
            candidates.append((piece, px, py))
    random.shuffle(candidates)

    for piece, px, py in candidates[:MAX_SHARDS]:
        dx, dy = (px - cx), (py - cy)
        ang = math.atan2(dy, dx) + random.uniform(-0.4, 0.4)
        spd = random.uniform(420, 820)
        vx = math.cos(ang) * spd;
        vy = math.sin(ang) * spd - random.uniform(140, 260)
        shards.append(Shard(piece, px, py, vx, vy, random.uniform(0, 360), random.uniform(-720, 720)))

    if override_color is not None:
        base = override_color
    else:
        c = surf.get_at((min(fw - 1, fw // 2), min(fh - 1, fh // 2)));
        base = (c.r, c.g, c.b)

    sparks = []
    for _ in range(SPARK_COUNT):
        ang = random.uniform(0, 2 * math.pi);
        spd = random.uniform(500, 1000)
        vx = math.cos(ang) * spd;
        vy = math.sin(ang) * spd - random.uniform(80, 180)
        life = random.uniform(0.18, 0.42);
        r = random.randint(2, 3)
        jitter = lambda v: max(0, min(255, int(v + random.uniform(-30, 30))))
        col = (jitter(base[0]), jitter(base[1]), jitter(base[2]))
        sparks.append(Spark(cx, cy, vx, vy, life, r, col))

    return (cx, cy), base, shards, sparks


def animate_explosion(screen, clock, draw_scene, target, override_color=None, *, fall_drop=False):
    """Standard-Explosion; optional zusätzliches Fallenlassen des ganzen Sprites (Frucht).
       WICHTIG: Ziel sofort aus der normalen Szene ausblenden, damit kein 'hängender' Frame bleibt.
    """
    (cx, cy), color, shards, sparks = make_explosion_from_surface(
        target.surf, target.x, target.y, override_color=override_color
    )

    # --- Ziel sofort verstecken, damit es NICHT mehr an der alten Stelle gezeichnet wird ---
    target.done = True

    # --- Zusatz: Fallenlassen der Frucht (nur wenn fall_drop=True) ---
    fall_img = None
    if fall_drop:
        fall_img   = target.surf
        fall_x     = float(target.x)
        fall_y     = float(target.y)
        fall_vy    = 0.0
        fall_angle = random.uniform(-8, 8)
        fall_omega = random.uniform(-120, 120)
        fall_alpha = 255
    # -----------------------------------------------------------------

    start = pygame.time.get_ticks(); last = start
    duration_ms = int(EXP_DURATION*1000)
    flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shock_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    while True:
        now = pygame.time.get_ticks(); dt = (now - last) / 1000.0; last = now
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: return False
        t = now - start  # ms

        # Physik
        for s in shards:
            s.vy += GRAVITY*dt; s.x += s.vx*dt; s.y += s.vy*dt; s.angle += s.omega*dt
            s.alpha = max(0, s.alpha - int(255*dt/EXP_DURATION))
        for sp in list(sparks):
            sp.life -= dt; sp.x += sp.vx*dt; sp.y += sp.vy*dt; sp.vx *= 0.985; sp.vy += GRAVITY*0.65*dt
            if sp.life <= 0: sparks.remove(sp)

        if fall_img is not None:
            fall_vy += GRAVITY * 0.75 * dt
            fall_y  += fall_vy * dt
            fall_angle += fall_omega * dt
            # t ist in ms -> mit duration_ms normieren
            fall_alpha = max(0, int(255 * (1.0 - min(1.0, t / duration_ms))))

        offset = shake_offset(t)
        draw_scene(scene_offset=offset)  # Szene ohne das versteckte Ziel

        if t < SHOCK_MS:
            shock_layer.fill((0,0,0,0))
            prog = t / SHOCK_MS
            r = int(20 + prog*140); a = max(0, int(180*(1.0-prog)))
            pygame.draw.circle(shock_layer, (255,255,255,a), (int(cx+offset[0]), int(cy+offset[1])), r, 4)
            screen.blit(shock_layer, (0,0))

        # fallende Frucht
        if fall_img is not None and fall_alpha > 0:
            img = pygame.transform.rotozoom(fall_img, -fall_angle, 1.0)
            img.set_alpha(fall_alpha)
            screen.blit(img, (int(fall_x + offset[0]), int(fall_y + offset[1])))

        # Scherben & Funken
        for s in shards:
            if s.alpha <= 0: continue
            img = pygame.transform.rotozoom(s.surf, -s.angle, 1.0); img.set_alpha(s.alpha)
            screen.blit(img, (int(s.x + offset[0]), int(s.y + offset[1])))
        for sp in sparks:
            if sp.life > 0:
                pygame.draw.circle(screen, sp.color, (int(sp.x + offset[0]), int(sp.y + offset[1])), sp.r)

        if t < FLASH_MS:
            flash.fill((255,255,255, int(220*(1.0 - t/FLASH_MS)))); screen.blit(flash, (0,0))

        pygame.display.flip(); clock.tick(FPS_LIMIT)
        if t > duration_ms: break

    return True



# ---------- Western-Hit: Explosion + Death gleichzeitig + Overlay-PNG ----------
def animate_west_hit(screen, clock, draw_scene_base, draw_overlays, draw_hud, target, death_fps=WEST_DEATH_FPS):
    (cx, cy), color, shards, sparks = make_explosion_from_surface(
        target.surf, target.x, target.y, override_color=(255, 40, 40)
    )
    frames = target.death_frames or []
    frame_ms = max(1, int(1000 / max(1, death_fps)))
    start = pygame.time.get_ticks();
    last = start
    max_dur = max(int(EXP_DURATION * 1000), len(frames) * frame_ms)

    flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shock_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    target.done = True

    while True:
        now = pygame.time.get_ticks();
        dt = (now - last) / 1000.0;
        last = now
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: return False
        t = now - start
        offset = shake_offset(t)

        # 1) Szene ohne Overlays/HUD
        screen.fill((0, 0, 0))
        draw_scene_base(offset)

        # 2) Explosion
        for s in shards:
            s.vy += GRAVITY * dt;
            s.x += s.vx * dt;
            s.y += s.vy * dt;
            s.angle += s.omega * dt
            s.alpha = max(0, s.alpha - int(255 * dt / EXP_DURATION))
            img = pygame.transform.rotozoom(s.surf, -s.angle, 1.0);
            img.set_alpha(s.alpha)
            screen.blit(img, (int(s.x + offset[0]), int(s.y + offset[1])))
        for sp in list(sparks):
            sp.life -= dt;
            sp.x += sp.vx * dt;
            sp.y += sp.vy * dt;
            sp.vx *= 0.985;
            sp.vy += GRAVITY * 0.65 * dt
            if sp.life > 0:
                pygame.draw.circle(screen, sp.color, (int(sp.x + offset[0]), int(sp.y + offset[1])), sp.r)
        if t < SHOCK_MS:
            shock_layer.fill((0, 0, 0, 0))
            prog = t / SHOCK_MS
            r = int(20 + prog * 140);
            a = max(0, int(180 * (1.0 - prog)))
            pygame.draw.circle(shock_layer, (255, 255, 255, a), (int(cx + offset[0]), int(cy + offset[1])), r, 4)
            screen.blit(shock_layer, (0, 0))
        if t < FLASH_MS:
            flash.fill((255, 255, 255, int(220 * (1.0 - t / FLASH_MS))));
            screen.blit(flash, (0, 0))

        # 3) Death-Frame entsprechend Zeit
        if frames:
            idx = min(len(frames) - 1, int(t // frame_ms))
            screen.blit(frames[idx], (int(target.x + offset[0]), int(target.y + offset[1])))

        # 4) PNG-Overlays (z.B. Geländer) OBEN DRAUF
        draw_overlays(offset)

        # 5) HUD zuletzt
        draw_hud(extra_cross=False, scene_offset=offset)

        pygame.display.flip()
        clock.tick(FPS_LIMIT)
        if t >= max_dur: break
    return True


# ---------------- Hauptprogramm ----------------
def main():
    pygame.init()
    hm_buttons(["x"] * 9)

    # feste 1366x768 (Fenster)
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1)
    except TypeError:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Elimination — Levels")
    clock = pygame.time.Clock()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    # Cursor-Grafik (Schuss)
    cross = load_img(os.path.join(ASSET_ROOT, "pics/Schuss.png"))
    cross_mask = pygame.mask.from_surface(cross)
    cross_pos, cross_until = None, 0

    # Spieler / Turnier
    original_players = hm_names() or ["flo", "kai", "alex", "stefan"]
    start_idx = random.randrange(len(original_players))
    active_players = original_players[start_idx:] + original_players[:start_idx]
    eliminated_set = set()
    current_player_idx = 0
    round_hits = [None] * len(active_players)

    # Fonts + HUD
    font_hud = pygame.font.Font(None, 64);
    font_hud.set_bold(True)
    font_title = pygame.font.Font(None, 40);
    font_title.set_bold(True)
    font_list = pygame.font.Font(None, 34)

    def outlined_cache(names, color):
        return {n: render_outlined(n, font_list, color) for n in names}

    name_white = outlined_cache(original_players, (255, 255, 255))
    name_yell = outlined_cache(original_players, (255, 240, 0))
    name_gray = outlined_cache(original_players, (190, 190, 190))
    title_surf = render_outlined("Spieler", font_title, (230, 230, 230))
    hud_cache = {}

    # Levels: WEST zuerst (Debug), dann BAUM
    level_idx = 0
    levels = [build_level2(), build_level1()]

    # --- Zeichen-Helfer ---
    def draw_scoreboard():
        x_right = WIDTH - RIGHT_INSET;
        y = 16
        r = title_surf.get_rect(topright=(x_right, y));
        screen.blit(title_surf, r)
        y = r.bottom + 8
        current_name = active_players[current_player_idx] if active_players else ""
        for name in original_players:
            surf = name_yell[name] if (name == current_name and name not in eliminated_set) \
                else (name_gray[name] if name in eliminated_set else name_white[name])
            rr = surf.get_rect(topright=(x_right, y));
            screen.blit(surf, rr)
            if name in eliminated_set:
                pygame.draw.line(screen, (230, 40, 40), (rr.left - 4, rr.centery), (rr.right, rr.centery), 3)
            y = rr.bottom + 6

    def draw_scene_base(scene_offset=(0, 0)):
        levels[level_idx].draw(screen, offset=scene_offset)

    def draw_overlays(scene_offset=(0, 0)):
        levels[level_idx].draw_overlays(screen, offset=scene_offset)

    def draw_hud(extra_cross=True, scene_offset=(0, 0)):
        ox, oy = int(scene_offset[0]), int(scene_offset[1])
        if extra_cross and cross_pos and pygame.time.get_ticks() < cross_until:
            screen.blit(cross, (int(cross_pos[0]) + ox, int(cross_pos[1]) + oy))
        label = f"Aktiver Spieler: {active_players[current_player_idx]}"
        if label not in hud_cache:
            hud_cache[label] = render_outlined(label, font_hud, (255, 255, 255))
        screen.blit(hud_cache[label], (12, 10))
        draw_scoreboard()

    def draw_scene(extra_cross=True, scene_offset=(0, 0)):
        screen.fill((0, 0, 0))
        draw_scene_base(scene_offset)
        draw_overlays(scene_offset)  # PNG-Overlays (Geländer etc.)
        draw_hud(extra_cross=extra_cross, scene_offset=scene_offset)

    def draw_scene_and_flip():
        draw_scene()
        pygame.display.flip()

    def show_winner(name):
        screen.fill((0, 0, 0))
        win = render_outlined("Winner:", font_hud, (255, 255, 255))
        who = render_outlined(name, font_hud, (255, 255, 0))
        screen.blit(win, (WIDTH // 2 - win.get_width() // 2, HEIGHT // 2 - 120))
        screen.blit(who, (WIDTH // 2 - who.get_width() // 2, HEIGHT // 2 - 40))
        pygame.display.flip()
        wait = True
        while wait:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    wait = False
                elif ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    wait = False
            clock.tick(30)

    def evaluate_shot(mx, my):
        nonlocal cross_pos, cross_until
        cross_pos = (mx - cross.get_width() // 2, my - cross.get_height() // 2)
        cross_until = pygame.time.get_ticks() + CROSS_FLASH_MS
        for t in levels[level_idx].targets:
            if t.done: continue
            off = (int(cross_pos[0]) - int(t.x), int(cross_pos[1]) - int(t.y))
            if t.mask.overlap(cross_mask, off):
                return True, t
        return False, None

    def animate_target_down(target):
        if levels[level_idx].name == "Wilder Westen":
            return animate_west_hit(screen, clock, draw_scene_base, draw_overlays, draw_hud, target,
                                    death_fps=WEST_DEATH_FPS)
        # Baum: Explosion + zusätzlich fallende Frucht
        return animate_explosion(screen, clock, draw_scene, target, fall_drop=True)

    def goto_next_level():
        nonlocal level_idx
        level_idx = (level_idx + 1) % len(levels)
        # neu betretenes Level frisch machen
        levels[level_idx].reset_targets()

    def advance_turn(hit, target_hit):
        nonlocal current_player_idx, active_players, round_hits, eliminated_set, hud_cache
        hud_cache.clear()
        if hit and target_hit:
            if not animate_target_down(target_hit): return False
            if levels[level_idx].all_down():
                goto_next_level()
        round_hits[current_player_idx] = bool(hit)
        current_player_idx += 1
        if current_player_idx < len(active_players): return True

        # Rundenende
        if len(active_players) > 2:
            if any(round_hits):
                new_active = [p for p, h in zip(active_players, round_hits) if h]
                eliminated_set.update(set(active_players) - set(new_active))
                active_players[:] = new_active
            round_hits[:] = [None] * len(active_players)
            current_player_idx = 0
            return True

        # Finale
        if len(active_players) == 2:
            a, b = round_hits
            if a and not b: eliminated_set.add(active_players[1]); show_winner(active_players[0]); return False
            if b and not a: eliminated_set.add(active_players[0]); show_winner(active_players[1]); return False
            round_hits[:] = [None, None];
            current_player_idx = 0;
            return True

        if len(active_players) == 1:
            show_winner(active_players[0]);
            return False
        return True

    # ---------------- Main Loop ----------------
    running = True
    while running and hm_game_active():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_n:
                goto_next_level()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                hit, t = evaluate_shot(mx, my)
                hm_screenshot(screen)
                running = advance_turn(hit, t)

        if running and hm_hit_detected():
            pos = hm_get_pos()
            if pos:
                mx, my = pos
                hit, t = evaluate_shot(mx, my)
                hm_screenshot(screen)
                running = advance_turn(hit, t)

        draw_scene_and_flip()
        clock.tick(FPS_LIMIT)

    pygame.quit()


if __name__ == "__main__":
    main()
