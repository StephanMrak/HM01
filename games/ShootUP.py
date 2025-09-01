# shootup_reaction_optimized.py — Reaction-Mode mit Death-Animation (Pi Zero 2 optimiert)
import os, random, pygame

# ---- optional: hmsysteme (RGB, Treffer-Input) --------------------------------
try:
    import hmsysteme
    HAS_HM = True
except Exception:
    HAS_HM = False

def hm_put_buttons(names):
    if HAS_HM and hasattr(hmsysteme, "put_button_names"):
        try: hmsysteme.put_button_names(names)
        except Exception: pass

def hm_rgb(rgb):
    if HAS_HM and hasattr(hmsysteme, "put_rgbcolor"):
        try: hmsysteme.put_rgbcolor(rgb)
        except Exception: pass

def hm_hit_detected():
    return HAS_HM and hasattr(hmsysteme, "hit_detected") and hmsysteme.hit_detected()

def hm_get_pos():
    if HAS_HM and hasattr(hmsysteme, "get_pos"):
        try: return hmsysteme.get_pos()
        except Exception: return None
    return None

# ---- Spiel-Config --------------------------------------------------------------
FPS_LIMIT      = 30
SPAWN_MIN_MS   = 1000   # 1 s
SPAWN_MAX_MS   = 5000   # 5 s
DEATH_FPS      = 12     # Death-Animation (Frames pro Sekunde)
DEATH_FALLBACK = 220    # ms – falls kein Death-Ordner existiert (kurzes „Zucken“)

ASSET_ROOT = os.path.dirname(os.path.realpath(__file__))

# Basis-Sprite pro Gegner + Ordner
ENEMIES = [
    ("Cow",           "pics/ShootUP/Cow",          "1.png"),   # kein Death-Ordner vorhanden? -> Fallback
    ("Mauler",        "pics/ShootUP/Mauler",       "0.png"),
    ("EarthElement",  "pics/ShootUP/EarthElement", "0x.png"),
    ("SwampCreature", "pics/ShootUP/SwampCreature","0.png"),
    ("Bullrog",       "pics/ShootUP/Ballrog",      "0.png"),
    ("Mercenary",     "pics/ShootUP/Mercenary",    "0.png"),
    ("Icemonster",    "pics/ShootUP/Icemonster",   "0.png"),
]

# Fixe Positionen (passen zu deinem Hintergrund)
POSITIONS = [
    (800,150), (750,210), (400,290),
    (650,250), (650,150), (300,150), (750,400)
]

# ---- Hilfsfunktionen -----------------------------------------------------------
def load_image(path):
    return pygame.image.load(path).convert_alpha()

def list_death_frames(folder):
    """Gibt sortierte Dateipfade für Death-Frames zurück (falls vorhanden)."""
    death_dir = os.path.join(ASSET_ROOT, folder, "Death")
    if not os.path.isdir(death_dir):
        return []
    files = [f for f in os.listdir(death_dir) if f.lower().endswith(".png")]
    # numerisch sortieren (Dateien heißen z.B. 1.png, 3.png, 10.png, ...)
    def key(f):
        name = os.path.splitext(f)[0]
        try:
            return int("".join(ch for ch in name if ch.isdigit()) or 0)
        except ValueError:
            return name
    files.sort(key=key)
    return [os.path.join(death_dir, f) for f in files]

def main():
    pygame.init()
    info = pygame.display.Info()
    SIZE = (info.current_w, info.current_h)  # z.B. 1366x768

    flags = pygame.FULLSCREEN | pygame.SCALED
    try:
        screen = pygame.display.set_mode(SIZE, flags, vsync=1)
    except TypeError:
        screen = pygame.display.set_mode(SIZE, flags)

    pygame.display.set_caption("ShootUP – Reaction Mode (Optimized)")
    clock = pygame.time.Clock()

    # Hintergrund/Overlay EINMALIG auf Bildschirmgröße skalieren
    bg_raw      = load_image(os.path.join(ASSET_ROOT, "pics/ShootUP/backgroundx.jpg"))
    overlay_raw = load_image(os.path.join(ASSET_ROOT, "pics/ShootUP/Overlay1.png"))
    bg      = pygame.transform.smoothscale(bg_raw, SIZE)
    overlay = pygame.transform.smoothscale(overlay_raw, SIZE)

    # Cross
    cross = load_image(os.path.join(ASSET_ROOT, "pics/ShootUP/Schuss.png"))
    cross_mask = pygame.mask.from_surface(cross)
    cross_show_until = 0
    last_cross_pos = None

    # Gegner: Basissprite + Maske (einmal)
    enemy_surfs, enemy_masks = [], []
    for _, folder, file in ENEMIES:
        surf = load_image(os.path.join(ASSET_ROOT, folder, file))
        enemy_surfs.append(surf)
        enemy_masks.append(pygame.mask.from_surface(surf))

    # Death-Cache (lazy)
    death_cache = {}  # enemy_index -> [surfaces]

    # Reihenfolgen
    remaining = list(range(len(ENEMIES)))
    random.shuffle(remaining)
    pos_pool = list(range(len(POSITIONS)))
    random.shuffle(pos_pool)

    # State
    EVT_SPAWN = pygame.USEREVENT + 1
    def schedule_next_spawn():
        if remaining:
            pygame.time.set_timer(EVT_SPAWN, random.randint(SPAWN_MIN_MS, SPAWN_MAX_MS), loops=1)

    current_enemy = None
    current_pos   = None
    current_mask  = None
    spawn_ticks   = 0
    waiting_for_click = False

    reaction_times = []  # (name, ms)

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, EVT_SPAWN])
    hm_put_buttons(["RESET","+","SCORE BOARD","<","Enter",">","BACK","-","BLIND SHOT"])
    schedule_next_spawn()

    running = True
    while running:
        now = pygame.time.get_ticks()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

            elif ev.type == EVT_SPAWN and remaining:
                idx = remaining.pop()
                current_enemy = idx
                current_mask  = enemy_masks[idx]
                pos_i = pos_pool.pop() if pos_pool else random.randrange(len(POSITIONS))
                current_pos = POSITIONS[pos_i]
                spawn_ticks = now
                waiting_for_click = True
                hm_rgb((140, 0, 140))  # bereit

            elif ev.type == pygame.MOUSEBUTTONDOWN and waiting_for_click and current_enemy is not None:
                mx, my = ev.pos
                last_cross_pos = (mx - cross.get_width()//2, my - cross.get_height()//2)
                cross_show_until = now + 120
                off = (last_cross_pos[0] - current_pos[0], last_cross_pos[1] - current_pos[1])
                if current_mask.overlap(cross_mask, off):
                    rt = now - spawn_ticks
                    reaction_times.append((ENEMIES[current_enemy][0], rt))
                    waiting_for_click = False
                    hm_rgb((0, 255, 0))
                    # Death-Animation für diesen Gegner
                    play_death(screen, clock, bg, overlay, current_enemy, current_pos,
                               enemy_surfs, death_cache)
                    current_enemy = None; current_pos = None; current_mask = None
                    schedule_next_spawn()
                else:
                    hm_rgb((255, 0, 0))

        # Hardware-Shooter (optional)
        if waiting_for_click and current_enemy is not None and hm_hit_detected():
            pos = hm_get_pos()
            if pos:
                mx, my = pos
                last_cross_pos = (mx - cross.get_width()//2, my - cross.get_height()//2)
                cross_show_until = now + 120
                off = (last_cross_pos[0] - current_pos[0], last_cross_pos[1] - current_pos[1])
                if current_mask.overlap(cross_mask, off):
                    rt = now - spawn_ticks
                    reaction_times.append((ENEMIES[current_enemy][0], rt))
                    waiting_for_click = False
                    hm_rgb((0, 255, 0))
                    play_death(screen, clock, bg, overlay, current_enemy, current_pos,
                               enemy_surfs, death_cache)
                    current_enemy = None; current_pos = None; current_mask = None
                    schedule_next_spawn()
                else:
                    hm_rgb((255, 0, 0))

        # Zeichnen
        screen.blit(bg, (0,0))
        if current_enemy is not None and current_pos is not None:
            screen.blit(enemy_surfs[current_enemy], current_pos)
        screen.blit(overlay, (0,0))
        if last_cross_pos and now < cross_show_until:
            screen.blit(cross, last_cross_pos)

        # HUD
        font = pygame.font.SysFont("Arial", 18)
        screen.blit(font.render(f"Verbleibend: {len(remaining)}   Gemessen: {len(reaction_times)}",
                                True, (255,255,255)), (10,10))

        pygame.display.flip()
        clock.tick(FPS_LIMIT)

        if not remaining and not waiting_for_click and current_enemy is None:
            running = False

    # Ergebnis
    total_ms = sum(t for _, t in reaction_times) if reaction_times else 0
    screen.fill((0,0,0))
    fontH = pygame.font.SysFont("Arial", 28, bold=True)
    font  = pygame.font.SysFont("Arial", 24)
    y = 60
    screen.blit(fontH.render("Ergebnis", True, (255,255,255)), (50,20))
    for name, t in reaction_times:
        screen.blit(font.render(f"{name}: {t/1000:.3f} s", True, (200,200,200)), (50,y))
        y += 32
    screen.blit(font.render("-"*30, True, (120,120,120)), (50,y)); y += 32
    screen.blit(font.render(f"Gesamtzeit (Score): {total_ms/1000:.3f} s", True, (255,255,0)), (50,y))
    pygame.display.flip()

    # warten bis Taste
    wait = True
    while wait:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: wait = False
            elif ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN: wait = False
        clock.tick(30)

# ---- Death-Animation -----------------------------------------------------------
def play_death(screen, clock, bg, overlay, enemy_idx, pos, enemy_surfs, death_cache):
    """Spielt die Death-Animation des getroffenen Gegners ab (lazy-loaded, 12fps)."""
    name, folder, _ = ENEMIES[enemy_idx]

    # Frames laden & cachen (nur beim ersten Treffer dieses Gegners)
    if enemy_idx not in death_cache:
        paths = list_death_frames(folder)
        if paths:
            death_cache[enemy_idx] = [load_image(p) for p in paths]
        else:
            death_cache[enemy_idx] = []  # kein Death-Ordner vorhanden

    frames = death_cache[enemy_idx]
    if not frames:
        # Kein Death-Ordner -> kurzer Fallback (z. B. kurzes „Wackeln“)
        t_end = pygame.time.get_ticks() + DEATH_FALLBACK
        base = enemy_surfs[enemy_idx]
        up   = 2
        while pygame.time.get_ticks() < t_end:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: return
            screen.blit(bg,(0,0)); screen.blit(base,(pos[0], pos[1]-up)); screen.blit(overlay,(0,0))
            pygame.display.flip()
            clock.tick(60)
            up = -up
        return

    frame_time = int(1000 / DEATH_FPS)
    for surf in frames:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: return
        screen.blit(bg, (0,0))
        screen.blit(surf, pos)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(frame_time)

if __name__ == "__main__":
    main()
