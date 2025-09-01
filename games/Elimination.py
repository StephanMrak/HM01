# Elimination_optimized.py — 1366x768 • HM+Maus • KO-Turnier
# Update: kräftige Explosion (Splitter + Funken + Flash + Shockwave + Screen-Shake), kein Rauch
import os, random, math, pygame

# -------- optionale hmsysteme-Wrapper --------
try:
    import hmsysteme
    HAS_HM = True
except Exception:
    HAS_HM = False

def hm_names():
    if HAS_HM and hasattr(hmsysteme, "get_playernames"):
        try: return hmsysteme.get_playernames()
        except Exception: pass
    return []

def hm_game_active():
    if HAS_HM and hasattr(hmsysteme, "game_isactive"):
        try: return hmsysteme.game_isactive()
        except Exception: pass
    return True

def hm_hit_detected():
    return HAS_HM and hasattr(hmsysteme, "hit_detected") and hmsysteme.hit_detected()

def hm_get_pos():
    if HAS_HM and hasattr(hmsysteme, "get_pos"):
        try: return hmsysteme.get_pos()
        except Exception: return None
    return None

def hm_screenshot(screen):
    if HAS_HM and hasattr(hmsysteme, "take_screenshot"):
        try: hmsysteme.take_screenshot(screen)
        except Exception: pass

def hm_buttons(labels):
    if HAS_HM and hasattr(hmsysteme, "put_button_names"):
        try: hmsysteme.put_button_names(labels)
        except Exception: pass

# -------- Konfiguration --------
WIDTH, HEIGHT  = 1366, 768
FPS_LIMIT      = 30
CROSS_FLASH_MS = 120

# Explosion-Feintuning (mehr "Wumms")
EXP_DURATION   = 0.9      # s gesamt
GRAVITY        = 1300.0   # px/s^2
MAX_SHARDS     = 32       # Splitter
SPARK_COUNT    = 70       # Funken/Juice
FLASH_MS       = 110      # kurzer Weißblitz
SHAKE_MS       = 220      # Screen-Shake-Dauer
SHAKE_AMPL     = 12       # max px
SHOCK_MS       = 280      # Schockwelle

RIGHT_INSET    = 90       # Spielernamen vom rechten Rand

ASSET_ROOT = os.path.dirname(os.path.realpath(__file__))

FRUITS_DEF = [
    ("Jackfruit",   "pics/Elimination/Groß/Jackfruitx.png", (110,159), (350,410)),
    ("Stinkfrucht", "pics/Elimination/Groß/Stinkfruchtx.png",(110,167), (550,470)),
    ("Ananas",      "pics/Elimination/Groß/Ananas.png",     (110,192), (750,430)),
    ("Sauersack",   "pics/Elimination/Groß/Sauersackx.png", (110,177), (950,410)),
    ("Kiwi",        "pics/Elimination/Mittel/Kiwi.png",      (80, 73), (510,310)),
    ("Birne",       "pics/Elimination/Mittel/Birne.png",     (70, 86), (660,310)),
    ("Bananen",     "pics/Elimination/Mittel/Bananen.png",  (110, 99), (360,250)),
    ("Apfel",       "pics/Elimination/Mittel/Apfel.png",     (70, 87), (940,260)),
    ("Orange",      "pics/Elimination/Mittel/Orange.png",    (85, 73), (790,310)),
    ("Himbeere",    "pics/Elimination/Klein/Himbeere.png",   (40, 50), (750,150)),
    ("Kirsche",     "pics/Elimination/Klein/Kirsche.png",    (50, 51), (630,150)),
    ("Brombeere",   "pics/Elimination/Klein/Brombeere.png",  (60, 77), (850,170)),
    ("Erdbeere",    "pics/Elimination/Klein/Erdbeere.png",   (60, 87), (510,160)),
]

# -------- Helpers --------
def load_img(path, size=None):
    surf = pygame.image.load(path).convert_alpha()
    if size:
        surf = pygame.transform.smoothscale(surf, size)
    return surf

def render_outlined(text, font, color, outline=(0,0,0), thick=1):
    base = font.render(text, True, color)
    outl = font.render(text, True, outline)
    w, h = base.get_width()+2*thick, base.get_height()+2*thick
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in (-thick, 0, thick):
        for dy in (-thick, 0, thick):
            if dx == 0 and dy == 0: continue
            surf.blit(outl, (dx+thick, dy+thick))
    surf.blit(base, (thick, thick))
    return surf

class Fruit:
    __slots__ = ("name","surf","mask","x","y0","y","hit","done")
    def __init__(self, name, surf, pos):
        self.name = name
        self.surf = surf
        self.mask = pygame.mask.from_surface(surf)
        self.x, self.y0 = pos
        self.y = self.y0
        self.hit = False
        self.done = False
    def reset(self):
        self.y = self.y0; self.hit = False; self.done = False
    def draw(self, screen, offset=(0,0)):
        if not self.done:
            screen.blit(self.surf, (self.x + offset[0], self.y + offset[1]))

# -------- Explosion --------
class Shard:
    __slots__ = ("surf","x","y","vx","vy","angle","omega","alpha")
    def __init__(self, surf, x, y, vx, vy, angle, omega):
        self.surf = surf
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.angle = angle
        self.omega = omega
        self.alpha = 255

class Spark:
    __slots__ = ("x","y","vx","vy","life","r","color")
    def __init__(self, x,y,vx,vy,life,r,color):
        self.x,self.y=x,y; self.vx,self.vy=vx,vy; self.life=life; self.r=r; self.color=color

def make_explosion_from_fruit(fruit):
    """Splitter+Funken aus Frucht: Center & Farbton ableiten."""
    shards = []
    fw, fh = fruit.surf.get_width(), fruit.surf.get_height()
    cx, cy = fruit.x + fw/2, fruit.y + fh/2

    # Kachelgröße dynamisch -> echte Fruchtstücke
    tile = max(10, min(20, min(fw, fh)//6))
    cols = max(1, fw // tile)
    rows = max(1, fh // tile)
    candidates = []
    for cyi in range(rows):
        for cxi in range(cols):
            rx, ry = cxi*tile, cyi*tile
            rect = pygame.Rect(rx, ry, tile, tile)
            sub = fruit.surf.subsurface(rect)
            br = sub.get_bounding_rect(min_alpha=10)
            if br.width == 0 or br.height == 0:
                continue
            piece = sub.subsurface(br).copy()
            px = fruit.x + rx + br.x
            py = fruit.y + ry + br.y
            candidates.append((piece, px, py))
    random.shuffle(candidates)

    for piece, px, py in candidates[:MAX_SHARDS]:
        # radial nach außen, mit Extra-Punch
        dx, dy = (px - cx), (py - cy)
        base_ang = math.atan2(dy, dx)
        ang  = base_ang + random.uniform(-0.4, 0.4)
        spd  = random.uniform(420, 820)        # schneller
        vx   = math.cos(ang)*spd
        vy   = math.sin(ang)*spd - random.uniform(140, 260)
        omega = random.uniform(-720, 720)      # schnelle Rotation
        angle = random.uniform(0, 360)
        shards.append(Shard(piece, px, py, vx, vy, angle, omega))

    # Farbton grob aus zentralem Pixel → Funkenfarbe
    c = fruit.surf.get_at((fw//2, fh//2))
    base = (c.r, c.g, c.b)
    sparks = []
    for _ in range(SPARK_COUNT):
        ang = random.uniform(0, 2*math.pi)
        spd = random.uniform(500, 1000)
        vx  = math.cos(ang)*spd
        vy  = math.sin(ang)*spd - random.uniform(80, 180)
        life = random.uniform(0.18, 0.42)
        r = random.randint(2, 3)
        jitter = lambda v: max(0,min(255,int(v + random.uniform(-30,30))))
        col = (jitter(base[0]), jitter(base[1]), jitter(base[2]))
        sparks.append(Spark(cx, cy, vx, vy, life, r, col))

    return (cx, cy), base, shards, sparks

def animate_explosion(screen, clock, draw_scene, fruit):
    """Kurze, kräftige Explosion mit Screen-Shake, Flash und Schockwelle."""
    (cx, cy), color, shards, sparks = make_explosion_from_fruit(fruit)
    start = pygame.time.get_ticks()
    last  = start
    duration_ms = int(EXP_DURATION*1000)

    # vorerzeugte Overlays
    flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shock_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    while True:
        now = pygame.time.get_ticks()
        dt = (now - last) / 1000.0
        last = now

        # ESC/QUIT zulassen
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: return False

        t = now - start

        # Physik
        for s in shards:
            s.vy += GRAVITY*dt
            s.x += s.vx*dt
            s.y += s.vy*dt
            s.angle += s.omega*dt
            s.alpha = max(0, s.alpha - int(255*dt/EXP_DURATION))

        for sp in sparks[:]:
            sp.life -= dt
            sp.x += sp.vx*dt
            sp.y += sp.vy*dt
            sp.vx *= 0.985
            sp.vy += GRAVITY*0.65*dt
            if sp.life <= 0: sparks.remove(sp)

        # Screen-Shake Offset (nur Szenerie, HUD bleibt stabil)
        if t < SHAKE_MS:
            amp = int(SHAKE_AMPL * (1.0 - t/ SHAKE_MS))
            offset = (random.randint(-amp, amp), random.randint(-amp, amp))
        else:
            offset = (0,0)

        # Grundszene
        draw_scene(scene_offset=offset)

        # Schockwelle (expandierender Ring, kurz)
        if t < SHOCK_MS:
            shock_layer.fill((0,0,0,0))
            prog = t / SHOCK_MS
            r = int(20 + prog*140)
            a = max(0, int(180*(1.0-prog)))
            col = (min(255, color[0]+40), min(255, color[1]+40), min(255, color[2]+40), a)
            pygame.draw.circle(shock_layer, col, (int(cx+offset[0]), int(cy+offset[1])), r, 4)
            screen.blit(shock_layer, (0,0))

        # Splitter
        for s in shards:
            if s.alpha <= 0: continue
            img = pygame.transform.rotozoom(s.surf, -s.angle, 1.0)
            img.set_alpha(s.alpha)
            screen.blit(img, (s.x + offset[0], s.y + offset[1]))

        # Funken (Saftspritzer)
        for sp in sparks:
            if sp.life > 0:
                pygame.draw.circle(screen, sp.color,
                                   (int(sp.x + offset[0]), int(sp.y + offset[1])), sp.r)

        # Flash (kurz Weißblende)
        if t < FLASH_MS:
            flash.fill((255,255,255, int(220*(1.0 - t/FLASH_MS))))
            screen.blit(flash, (0,0))

        pygame.display.flip()
        clock.tick(FPS_LIMIT)

        if t > duration_ms:
            break

    fruit.done = True
    return True

# -------- Hauptprogramm --------
def main():
    pygame.init()
    hm_buttons(["x"]*9)

    flags = pygame.FULLSCREEN | pygame.SCALED
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1)
    except TypeError:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Elimination — Fruits Knockout")
    clock = pygame.time.Clock()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    # Hintergrund & Assets
    bg = pygame.transform.smoothscale(load_img(os.path.join(ASSET_ROOT, "pics/Elimination/Baum.png")), (WIDTH, HEIGHT))
    cross = load_img(os.path.join(ASSET_ROOT, "pics/Schuss.png"))
    cross_mask = pygame.mask.from_surface(cross)
    cross_pos, cross_until = None, 0

    fruits = [Fruit(name, load_img(os.path.join(ASSET_ROOT, rel), size), pos)
              for name, rel, size, pos in FRUITS_DEF]

    def reset_all_fruits():
        for f in fruits: f.reset()
    def all_fruits_down():
        return all(f.done for f in fruits)

    # Spieler / Turnier
    original_players = hm_names() or ["flo", "kai", "alex", "stefan"]
    start_idx = random.randrange(len(original_players))
    active_players = original_players[start_idx:] + original_players[:start_idx]
    eliminated_set = set()
    current_player_idx = 0
    round_hits = [None] * len(active_players)

    # Fonts + Caches
    font_hud   = pygame.font.Font(None, 64); font_hud.set_bold(True)
    font_title = pygame.font.Font(None, 40); font_title.set_bold(True)
    font_list  = pygame.font.Font(None, 34)

    hud_cache = {}
    def outlined_cache(names, color):
        return {n: render_outlined(n, font_list, color) for n in names}
    name_white = outlined_cache(original_players, (255,255,255))
    name_yell  = outlined_cache(original_players, (255,240,0))
    name_gray  = outlined_cache(original_players, (190,190,190))
    title_surf = render_outlined("Spieler", font_title, (230,230,230))

    def draw_scoreboard():
        x_right = WIDTH - RIGHT_INSET
        y = 16
        r = title_surf.get_rect(topright=(x_right, y))
        screen.blit(title_surf, r)
        y = r.bottom + 8
        current_name = active_players[current_player_idx] if active_players else ""
        for name in original_players:
            surf = name_yell[name] if (name == current_name and name not in eliminated_set) \
                   else (name_gray[name] if name in eliminated_set else name_white[name])
            rr = surf.get_rect(topright=(x_right, y))
            screen.blit(surf, rr)
            if name in eliminated_set:
                pygame.draw.line(screen, (230,40,40), (rr.left-4, rr.centery), (rr.right, rr.centery), 3)
            y = rr.bottom + 6

    def draw_scene(extra_cross=True, scene_offset=(0,0)):
        # Szene (Hintergrund + Früchte), optional mit Shake-Offset
        screen.fill((0,0,0))
        screen.blit(bg, scene_offset)
        for f in fruits: f.draw(screen, offset=scene_offset)
        if extra_cross and cross_pos and pygame.time.get_ticks() < cross_until:
            screen.blit(cross, (cross_pos[0] + scene_offset[0], cross_pos[1] + scene_offset[1]))
        # HUD stabil ohne Shake
        label = f"Aktiver Spieler: {active_players[current_player_idx]}"
        if label not in hud_cache:
            hud_cache[label] = render_outlined(label, font_hud, (255,255,255))
        screen.blit(hud_cache[label], (12, 10))
        draw_scoreboard()

    def draw_scene_and_flip():
        draw_scene()
        pygame.display.flip()

    def show_winner(name):
        screen.fill((0,0,0))
        win = render_outlined("Winner:", font_hud, (255,255,255))
        who = render_outlined(name,        font_hud, (255,255,0))
        screen.blit(win, (WIDTH//2 - win.get_width()//2, HEIGHT//2 - 120))
        screen.blit(who, (WIDTH//2 - who.get_width()//2, HEIGHT//2 - 40))
        pygame.display.flip()
        wait = True
        while wait:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: wait = False
                elif ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN: wait = False
            clock.tick(30)

    def evaluate_shot(mx, my):
        nonlocal cross_pos, cross_until
        cross_pos = (mx - cross.get_width()//2, my - cross.get_height()//2)
        cross_until = pygame.time.get_ticks() + CROSS_FLASH_MS
        for f in fruits:
            if f.done: continue
            off = (cross_pos[0] - f.x, cross_pos[1] - f.y)
            if f.mask.overlap(cross_mask, off):
                f.hit = True
                return True, f
        return False, None

    def reset_tree_if_needed():
        if all_fruits_down():
            for f in fruits: f.reset()

    def advance_turn(hit, fruit_hit):
        nonlocal current_player_idx, active_players, round_hits, eliminated_set, hud_cache
        hud_cache.clear()
        if hit and fruit_hit:
            if not animate_explosion(screen, clock, draw_scene, fruit_hit): return False
            reset_tree_if_needed()

        round_hits[current_player_idx] = bool(hit)
        current_player_idx += 1
        if current_player_idx < len(active_players):
            return True

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
            if a and not b:
                eliminated_set.add(active_players[1]); show_winner(active_players[0]); return False
            if b and not a:
                eliminated_set.add(active_players[0]); show_winner(active_players[1]); return False
            round_hits[:] = [None, None]; current_player_idx = 0; return True

        if len(active_players) == 1:
            show_winner(active_players[0]); return False
        return True

    # -------- Main Loop --------
    reset_all_fruits()
    running = True
    while running and hm_game_active():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                hit, f = evaluate_shot(mx, my)
                hm_screenshot(screen)
                running = advance_turn(hit, f)
        # HM parallel
        if running and hm_hit_detected():
            pos = hm_get_pos()
            if pos:
                mx, my = pos
                hit, f = evaluate_shot(mx, my)
                hm_screenshot(screen)
                running = advance_turn(hit, f)

        draw_scene_and_flip()
        clock.tick(FPS_LIMIT)

    pygame.quit()

if __name__ == "__main__":
    main()
