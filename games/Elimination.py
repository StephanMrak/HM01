# Elimination.py — 1366x768 • HM+Maus • KO-Turnier
# Levels: Baum (Früchte), West (Gangsta), Ship (4 Bosse + Zombie mit Grid-Atlas)
# Zombie-Atlanten: Zombie/zombie_walk.json, Zombie/zombie_death.json (schema "grid-v1")

import os, math, random, json, pygame

# ---------- optionale HM-Systeme ----------
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
        except Exception: pass
    return None

def hm_screenshot(screen):
    if HAS_HM and hasattr(hmsysteme, "take_screenshot"):
        try: hmsysteme.take_screenshot(screen)
        except Exception: pass

def hm_buttons(labels):
    if HAS_HM and hasattr(hmsysteme, "put_button_names"):
        try: hmsysteme.put_button_names(labels)
        except Exception: pass

# ---------- Konfiguration ----------
WIDTH, HEIGHT = 1366, 768
FPS_LIMIT = 30
CROSS_FLASH_MS = 120
RIGHT_INSET = 90
ASSET_ROOT = os.path.dirname(os.path.realpath(__file__))

# Explosion
EXP_DURATION = 0.9
GRAVITY = 1300.0
MAX_SHARDS = 32
SPARK_COUNT = 70
FLASH_MS = 110
SHAKE_MS = 220
SHAKE_AMPL = 12
SHOCK_MS = 280

# ---- Death-Animation-Geschwindigkeit (Frames pro Sekunde) je Figur-Klasse ----
# Kleiner = langsamer. Alles hier zentral einstellbar.
DEATH_FPS_BY_CLASS = {
    "gangsta":      3,   # Wilder Westen
    "zombie":       9,   # Ship-Zombie (Atlas)
    "ballrog":      9,   # Ship-Bosse (Einzel-PNG-Sequenzen)
    "earthelement": 9,
    "icemonster":   9,
    "mauler":       9,
    "default":      9,   # Fallback
}


# ---------- Helfer ----------
def try_load_img(path):
    if not path: return None
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None

def load_img(path, size=None, placeholder=None):
    surf = try_load_img(path)
    if surf is None:
        if placeholder is None:
            surf = pygame.Surface((80,80), pygame.SRCALPHA)
            pygame.draw.circle(surf, (30,200,60), (40,40), 36)
            pygame.draw.circle(surf, (255,255,255), (40,40), 36, 2)
        else:
            surf = placeholder
    if size:
        surf = pygame.transform.smoothscale(surf, size)
    return surf

def render_outlined(text, font, color, outline=(0,0,0), thick=2):
    base = font.render(text, True, color)
    outl  = font.render(text, True, outline)
    w, h  = base.get_width()+2*thick, base.get_height()+2*thick
    surf  = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in (-thick, 0, thick):
        for dy in (-thick, 0, thick):
            if dx == 0 and dy == 0: continue
            surf.blit(outl, (dx+thick, dy+thick))
    surf.blit(base, (thick, thick))
    return surf

def shake_offset(ms_since_start: int) -> tuple[int,int]:
    if ms_since_start >= SHAKE_MS: return (0,0)
    k = 1.0 - (ms_since_start / SHAKE_MS)
    amp = max(0, int(SHAKE_AMPL * k))
    return (random.randint(-amp, amp), random.randint(-amp, amp))

def get_death_fps_for(level_name: str, target) -> int:
    """Liest (1) per-Target-Override, sonst (2) Klassen-Standard aus DEATH_FPS_BY_CLASS."""
    # 1) Per-Target-Override erlaubt (falls gesetzt)
    fps = getattr(target, "death_fps", None)
    if isinstance(fps, (int, float)) and fps > 0:
        return int(fps)

    # 2) Klassen-Standard
    if target.__class__.__name__ == "Zombie":
        return DEATH_FPS_BY_CLASS.get("zombie", DEATH_FPS_BY_CLASS["default"])

    if level_name == "Wilder Westen":
        return DEATH_FPS_BY_CLASS.get("gangsta", DEATH_FPS_BY_CLASS["default"])

    if level_name == "DeathShip":
        key = (getattr(target, "name", "") or "").lower()
        return DEATH_FPS_BY_CLASS.get(key, DEATH_FPS_BY_CLASS["default"])

    return DEATH_FPS_BY_CLASS["default"]

# ---------- Grid-Atlas Loader (schema: "grid-v1") ----------
def load_grid_atlas(json_path, image_dir):
    """
    Erwartet:
      {
        "meta": {"image": "zWalk.png", "schema": "grid-v1"},
        "grid": {
          "dirs": ["N","NE","E","SE","S","SW","W","NW"],
          "frames_per_dir": 8,
          "order": "row-major",
          "trim": false
        }
      }
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("meta", {})
    if meta.get("schema") != "grid-v1":
        raise ValueError("Atlas schema != grid-v1")
    image_name = meta["image"]
    grid = data["grid"]
    dirs = grid["dirs"]
    fpd  = int(grid["frames_per_dir"])

    sheet = try_load_img(os.path.join(image_dir, image_name))
    if sheet is None:
        raise FileNotFoundError(image_name)

    rows = len(dirs)
    cols = fpd
    fw = sheet.get_width()  // cols
    fh = sheet.get_height() // rows

    # Frames je Richtung
    by_dir = {}
    for r, d in enumerate(dirs):
        seq = []
        for c in range(cols):
            rect = pygame.Rect(c*fw, r*fh, fw, fh)
            seq.append(sheet.subsurface(rect).copy())
        by_dir[d] = seq

    return {"sheet": sheet, "dirs": dirs, "frames": by_dir, "fw": fw, "fh": fh}

# ---------- Ziele / Level ----------
class Target:
    __slots__ = ("name","surf","mask","x","y","done","death_frames")
    def __init__(self, name, surf, pos, death_frames=None):
        self.name = name
        self.surf = surf
        self.mask = pygame.mask.from_surface(surf)
        self.x, self.y = pos
        self.done = False
        self.death_frames = death_frames or []

    def reset(self): self.done = False

    def draw(self, screen, offset=(0,0)):
        if not self.done:
            screen.blit(self.surf, (int(self.x+offset[0]), int(self.y+offset[1])))

class Level:
    def __init__(self, name, bg_rel_path):
        self.name = name
        self.bg_path = os.path.join(ASSET_ROOT, bg_rel_path)
        self.bg = None
        self.targets = []
        self.overlays = []

    def load_bg(self):
        raw = try_load_img(self.bg_path)
        self.bg = pygame.transform.smoothscale(raw, (WIDTH, HEIGHT)) if raw else pygame.Surface((WIDTH,HEIGHT))

    def all_down(self): return all(t.done for t in self.targets)

    def draw(self, screen, offset=(0,0)):
        screen.blit(self.bg, offset)
        for t in self.targets: t.draw(screen, offset)

    def draw_overlays(self, screen, offset=(0,0)):
        for ov in self.overlays:
            screen.blit(ov[0], (ov[1][0]+offset[0], ov[1][1]+offset[1]))

# ---------- Level 1: Baum ----------
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
def build_level_baum():
    L = Level("Baum", "pics/Elimination/Baum.png")
    L.load_bg()
    L.targets = []
    for name, rel, size, pos in FRUITS_DEF:
        surf = load_img(os.path.join(ASSET_ROOT, rel), size)
        L.targets.append(Target(name, surf, pos))
    return L

# ---------- Level West ----------
WEST_BG   = "pics/Elimination/West/Background.png"
GANGSTA_DIR = "pics/Elimination/West/Gangsta"
GANGSTA_SPOTS = [
    (145, 255, 2.3),
    (70,  455, 2.5),
    (350, 510, 1.3),
    (550, 550, 0.55),
    (770, 500, 1.3),
    (1148,200, 2.5),
    (1050,450, 2.5),
    (560, 450, 3.30),
]
def load_gangsta_sequence():
    idle = load_img(os.path.join(ASSET_ROOT, GANGSTA_DIR, "1.png"))
    frames=[]
    for i in range(2,60):
        p=os.path.join(ASSET_ROOT,GANGSTA_DIR,f"{i}.png")
        if os.path.exists(p): frames.append(load_img(p))
        else: break
    return idle, frames

def build_level_west():
    L = Level("Wilder Westen", WEST_BG)
    L.load_bg()
    ov_path = os.path.join(ASSET_ROOT, "pics/Elimination/West/Overlays/left_balcony.png")
    ov = try_load_img(ov_path)
    if ov: L.overlays.append((ov, (0,0)))
    idle, deaths = load_gangsta_sequence()
    for i, (x,y,s) in enumerate(GANGSTA_SPOTS, 1):
        idl = pygame.transform.rotozoom(idle, 0, s)
        dfs = [pygame.transform.rotozoom(f, 0, s) for f in deaths]
        L.targets.append(Target(f"Gangsta {i}", idl, (x,y), dfs))
    return L

# ---------- Level Ship ----------
SHIP_BG   = "pics/Elimination/Ship/Background.png"
SHIP_DIR  = os.path.join(ASSET_ROOT, "pics/Elimination/Ship")
ZOMBIE_DIR = os.path.join(SHIP_DIR, "Zombie")
ZOMBIE_WALK_JSON  = os.path.join(ZOMBIE_DIR, "zombie_walk.json")
ZOMBIE_DEATH_JSON = os.path.join(ZOMBIE_DIR, "zombie_death.json")

def load_dir_deaths(folder):
    idle = load_img(os.path.join(folder, "0.png"))
    deaths=[]
    for i in range(1,200):
        p=os.path.join(folder,f"{i}.png")
        if os.path.exists(p): deaths.append(load_img(p))
        else: break
    return idle, deaths

class Zombie:
    DIRS = ["N","NE","E","SE","S","SW","W","NW"]
    def __init__(self, x, y, scale, walk_atlas, death_atlas):
        self.x,self.y = float(x), float(y)
        self.scale = scale
        self.walk  = walk_atlas
        self.death = death_atlas
        self.dir = "S"
        self.frame = 0
        self.time_acc = 0.0
        self.dead = False
        self.dead_frame = 0
        self.speed = 90.0
        self.mask = pygame.mask.from_surface(self.walk["frames"][self.dir][0])
        self.path = [(585,540),(720,540),(720,485),(610,485),(610,560),(585,540)]
        self.next_i = 1
        if abs(scale-1.0)>1e-3:
            for a in (self.walk,self.death):
                for d in a["frames"]:
                    a["frames"][d] = [pygame.transform.rotozoom(f,0,scale) for f in a["frames"][d]]

    def _dir_from_vec(self, dx, dy):
        ang = (math.degrees(math.atan2(-dy, dx)) + 360.0) % 360.0
        if   22.5<=ang<67.5:  return "NE"
        elif 67.5<=ang<112.5: return "N"
        elif 112.5<=ang<157.5:return "NW"
        elif 157.5<=ang<202.5:return "W"
        elif 202.5<=ang<247.5:return "SW"
        elif 247.5<=ang<292.5:return "S"
        elif 292.5<=ang<337.5:return "SE"
        else:                 return "E"

    def update(self, dt):
        if self.dead: return
        tx,ty = self.path[self.next_i]
        dx,dy = tx-self.x, ty-self.y
        dist = math.hypot(dx,dy)
        if dist < 4:
            self.next_i = (self.next_i+1)%len(self.path)
        else:
            self.dir = self._dir_from_vec(dx,dy)
            vx,vy = dx/dist*self.speed, dy/dist*self.speed
            self.x += vx*dt; self.y += vy*dt
            self.time_acc += dt
            if self.time_acc>0.08:
                self.time_acc=0; self.frame=(self.frame+1)%len(self.walk["frames"][self.dir])
        self.mask = pygame.mask.from_surface(self.walk["frames"][self.dir][self.frame])

    def draw(self, screen, offset=(0,0)):
        if self.dead:
            frames = self.death["frames"][self.dir]
            i = min(self.dead_frame, len(frames)-1)
            screen.blit(frames[i], (int(self.x+offset[0]), int(self.y+offset[1])))
        else:
            frame = self.walk["frames"][self.dir][self.frame]
            screen.blit(frame, (int(self.x+offset[0]), int(self.y+offset[1])))

    def kill(self):  # nur Status setzen, simultane Animation übernimmt das Rendering
        self.dead = True
        self.dead_frame = 0

    def done(self):
        return self.dead and self.dead_frame >= len(self.death["frames"][self.dir])-1

class ShipLevel(Level):
    def __init__(self):
        super().__init__("DeathShip", SHIP_BG)
        self.load_bg()
        self.targets = []
        for name in ("Ballrog","EarthElement","Icemonster","Mauler"):
            base = os.path.join(SHIP_DIR, name)
            idle, deaths = load_dir_deaths(base)
            x = 380 + len(self.targets)*160
            y = 420
            self.targets.append(Target(name, idle, (x,y), deaths))
        self.zombie_spawned = False
        self.zombie = None
        self.hide_zombie = False
        self.z_walk  = load_grid_atlas(ZOMBIE_WALK_JSON,  ZOMBIE_DIR)
        self.z_death = load_grid_atlas(ZOMBIE_DEATH_JSON, ZOMBIE_DIR)

    def spawn_zombie(self):
        if self.zombie_spawned: return
        self.zombie_spawned = True
        self.zombie = Zombie(585, 540, 1.3, self.z_walk, self.z_death)

    def update(self, dt):
        if self.zombie and not self.hide_zombie:
            self.zombie.update(dt)

    def draw(self, screen, offset=(0,0)):
        super().draw(screen, offset)
        if self.zombie and not self.hide_zombie:
            self.zombie.draw(screen, offset)

    def all_down(self):
        if self.zombie and not self.zombie.done(): return False
        if not all(t.done for t in self.targets): return False
        if not self.zombie_spawned:
            self.spawn_zombie()
            return False
        return True

# ---------- Explosion / Effekte ----------
class Shard:
    __slots__=("surf","x","y","vx","vy","angle","omega","alpha")
    def __init__(self,surf,x,y,vx,vy,angle,omega):
        self.surf=surf; self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.angle=angle; self.omega=omega; self.alpha=255

class Spark:
    __slots__=("x","y","vx","vy","life","r","color")
    def __init__(self,x,y,vx,vy,life,r,color):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy; self.life=life; self.r=r; self.color=color

def make_explosion_from_surface(surf, world_x, world_y, override_color=None):
    shards=[]
    fw,fh=surf.get_width(), surf.get_height()
    cx,cy = world_x+fw/2, world_y+fh/2
    tile = max(10, min(20, min(fw,fh)//6))
    cols=max(1, fw//tile); rows=max(1, fh//tile)
    cands=[]
    for r in range(rows):
        for c in range(cols):
            rx,ry=c*tile,r*tile
            sub=surf.subsurface(pygame.Rect(rx,ry,tile,tile))
            br=sub.get_bounding_rect(min_alpha=10)
            if br.w==0 or br.h==0: continue
            piece=sub.subsurface(br).copy()
            px,py=world_x+rx+br.x, world_y+ry+br.y
            cands.append((piece,px,py))
    random.shuffle(cands)
    for piece,px,py in cands[:MAX_SHARDS]:
        dx,dy = px-cx, py-cy
        ang=math.atan2(dy,dx)+random.uniform(-0.4,0.4)
        spd=random.uniform(420,820)
        vx=math.cos(ang)*spd; vy=math.sin(ang)*spd-random.uniform(140,260)
        shards.append(Shard(piece,px,py,vx,vy,random.uniform(0,360),random.uniform(-720,720)))
    if override_color is None:
        c=surf.get_at((min(fw-1,fw//2), min(fh-1,fh//2))); base=(c.r,c.g,c.b)
    else:
        base=override_color
    sparks=[]
    for _ in range(SPARK_COUNT):
        ang=random.uniform(0,2*math.pi); spd=random.uniform(500,1000)
        vx=math.cos(ang)*spd; vy=math.sin(ang)*spd-random.uniform(80,180)
        life=random.uniform(0.18,0.42); r=random.randint(2,3)
        jitter=lambda v:max(0,min(255,int(v+random.uniform(-30,30))))
        col=(jitter(base[0]), jitter(base[1]), jitter(base[2]))
        sparks.append(Spark(cx,cy,vx,vy,life,r,col))
    return (cx,cy), base, shards, sparks

# --- generische Simultan-Animation: Explosion + Death-Frames gleichzeitig ---
def animate_simul_explosion_death(screen, clock, draw_bg, death_frames, pos, surf_for_explosion,
                                  override_color=(255,40,40), death_fps=9, overlay_top_fn=None):
    """
    draw_bg(offset)   -> zeichnet Szene OHNE Standbild des Ziels
    death_frames      -> Liste mit Frames
    pos               -> (x,y) der Death-Sequenz
    surf_for_explosion-> Surface, die für die Explosion zerlegt wird
    overlay_top_fn    -> optionaler Callback, um Overlays nach oben zu blitten (z.B. Balkon)
    """
    (cx,cy), color, shards, sparks = make_explosion_from_surface(surf_for_explosion, pos[0], pos[1], override_color)
    start = pygame.time.get_ticks(); last = start
    frame_ms = max(1, int(1000/max(1,death_fps)))
    flash = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
    shock = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
    max_dur = max(int(EXP_DURATION*1000), len(death_frames)*frame_ms)

    while True:
        now=pygame.time.get_ticks(); dt=(now-last)/1000.0; last=now
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return False
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: return False
        t = now - start
        offset = shake_offset(t)

        # Update Explosionsteile
        for s in shards:
            s.vy+=GRAVITY*dt; s.x+=s.vx*dt; s.y+=s.vy*dt; s.angle+=s.omega*dt
            s.alpha=max(0, s.alpha-int(255*dt/EXP_DURATION))
        for sp in list(sparks):
            sp.life-=dt; sp.x+=sp.vx*dt; sp.y+=sp.vy*dt; sp.vx*=0.985; sp.vy+=GRAVITY*0.65*dt
            if sp.life<=0: sparks.remove(sp)

        draw_bg(offset)  # ohne Standbild

        # Shockring + Flash
        if t < SHOCK_MS:
            shock.fill((0,0,0,0))
            prog=t/SHOCK_MS; r=int(20+prog*140); a=max(0,int(180*(1.0-prog)))
            pygame.draw.circle(shock,(255,255,255,a),(int(cx+offset[0]),int(cy+offset[1])), r, 4)
            screen.blit(shock,(0,0))

        # Explosionsteile
        for s in shards:
            if s.alpha<=0: continue
            img=pygame.transform.rotozoom(s.surf,-s.angle,1.0); img.set_alpha(s.alpha)
            screen.blit(img,(int(s.x+offset[0]), int(s.y+offset[1])))
        for sp in sparks:
            pygame.draw.circle(screen, (255,60,60), (int(sp.x+offset[0]), int(sp.y+offset[1])), sp.r)

        if t<FLASH_MS:
            flash.fill((255,255,255,int(220*(1.0-t/FLASH_MS)))); screen.blit(flash,(0,0))

        # Death-Frame passend zur Zeit
        idx = min(len(death_frames)-1, t // frame_ms)
        screen.blit(death_frames[int(idx)], (int(pos[0]+offset[0]), int(pos[1]+offset[1])))

        # ggf. Overlay (Balkon) OBEN drauf
        if overlay_top_fn: overlay_top_fn(offset)

        pygame.display.flip()
        clock.tick(FPS_LIMIT)
        if t >= max_dur: break
    return True

# ---------- Spiel ----------
def main():
    pygame.init()
    hm_buttons(["x"]*9)
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1)
    except TypeError:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Elimination — Levels")
    clock = pygame.time.Clock()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    cross = load_img(os.path.join(ASSET_ROOT, "pics/Schuss.png"))
    cross_mask = pygame.mask.from_surface(cross)
    cross_pos, cross_until = None, 0

    # Spieler
    original_players = hm_names() or ["flo","kai","alex","stefan"]
    start_idx = random.randrange(len(original_players))
    active_players = original_players[start_idx:] + original_players[:start_idx]
    eliminated_set=set(); current_player_idx=0; round_hits=[None]*len(active_players)

    # Fonts + HUD
    font_title = pygame.font.Font(None, 64); font_title.set_bold(True)
    font_list  = pygame.font.Font(None, 38)
    def outlined_cache(names, color): return {n: render_outlined(n, font_list, color) for n in names}
    name_white = outlined_cache(original_players,(255,255,255))
    name_yell  = outlined_cache(original_players,(255,240,0))
    name_gray  = outlined_cache(original_players,(190,190,190))
    title_surf = render_outlined("Spieler", pygame.font.Font(None, 72), (255,255,255))

    # Levels: Ship, West, Baum
    levels=[ShipLevel(), build_level_west(), build_level_baum()]
    level_idx=0

    def draw_scoreboard():
        x_right=WIDTH-RIGHT_INSET; y=16
        r=title_surf.get_rect(topright=(x_right,y)); screen.blit(title_surf,r)
        y=r.bottom+8
        current_name = active_players[current_player_idx] if active_players else ""
        for name in original_players:
            surf = name_yell[name] if (name==current_name and name not in eliminated_set) \
                   else (name_gray[name] if name in eliminated_set else name_white[name])
            rr=surf.get_rect(topright=(x_right,y)); screen.blit(surf,rr)
            if name in eliminated_set:
                pygame.draw.line(screen,(230,40,40),(rr.left-4, rr.centery),(rr.right, rr.centery),4)
            y=rr.bottom+6

    def draw_base(offset=(0,0)):
        screen.fill((0,0,0))
        levels[level_idx].draw(screen, offset)
        if hasattr(levels[level_idx],"draw_overlays"): levels[level_idx].draw_overlays(screen, offset)
        if cross_pos and pygame.time.get_ticks()<cross_until:
            screen.blit(cross, (int(cross_pos[0]+offset[0]), int(cross_pos[1]+offset[1])))
        draw_scoreboard()

    def draw_scene_and_flip():
        draw_base((0,0))
        pygame.display.flip()

    def show_winner(name):
        f=pygame.font.Font(None, 96)
        w=render_outlined("Winner:", f,(255,255,255)); who=render_outlined(name,f,(255,255,0))
        screen.fill((0,0,0)); screen.blit(w,(WIDTH//2-w.get_width()//2, HEIGHT//2-120))
        screen.blit(who,(WIDTH//2-who.get_width()//2, HEIGHT//2-20)); pygame.display.flip()
        wait=True
        while wait:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: wait=False
                elif ev.type in (pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN): wait=False
            clock.tick(30)

    def evaluate_shot(mx,my):
        nonlocal cross_pos, cross_until
        cross_pos=(mx-cross.get_width()//2, my-cross.get_height()//2)
        cross_until=pygame.time.get_ticks()+CROSS_FLASH_MS
        # Zombie zuerst prüfen (falls sichtbar)
        if isinstance(levels[level_idx], ShipLevel) and levels[level_idx].zombie and not levels[level_idx].hide_zombie:
            z=levels[level_idx].zombie
            off=(int(cross_pos[0]-z.x), int(cross_pos[1]-z.y))
            if z.mask.overlap(cross_mask, off): return True, z
        for t in levels[level_idx].targets:
            if t.done: continue
            off=(int(cross_pos[0]-t.x), int(cross_pos[1]-t.y))
            if t.mask.overlap(cross_mask, off): return True, t
        return False, None

    def goto_next_level():
        nonlocal level_idx
        level_idx=(level_idx+1)%len(levels)

    def animate_explosion(screen, clock, draw_scene_wo, target, override_color=None):
        """Explosion + (bei Früchten zusätzlich Fall) – draw_scene_wo zeichnet Szene OHNE das getroffene Target."""
        (cx, cy), color, shards, sparks = make_explosion_from_surface(target.surf, target.x, target.y, override_color)
        start = pygame.time.get_ticks();
        last = start
        duration_ms = int(EXP_DURATION * 1000)
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shock = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Standbild sofort ausblenden (kein Doppelbild)
        target.done = True

        # „Frucht“-Heuristik: hat keine death_frames → fällt zusätzlich runter
        is_fruit = not getattr(target, "death_frames",
                               []) and "Gangsta" not in target.name and "Ship" not in target.name
        fall_y = float(target.y);
        fall_v = 0.0

        while True:
            now = pygame.time.get_ticks();
            dt = (now - last) / 1000.0;
            last = now;
            t = now - start
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: return False

            # Physik
            for s in shards:
                s.vy += GRAVITY * dt;
                s.x += s.vx * dt;
                s.y += s.vy * dt;
                s.angle += s.omega * dt
                s.alpha = max(0, s.alpha - int(255 * dt / EXP_DURATION))
            for sp in list(sparks):
                sp.life -= dt;
                sp.x += sp.vx * dt;
                sp.y += sp.vy * dt;
                sp.vx *= 0.985;
                sp.vy += GRAVITY * 0.65 * dt
                if sp.life <= 0: sparks.remove(sp)

            if is_fruit:
                fall_v += GRAVITY * dt
                fall_y += fall_v * dt

            offset = shake_offset(t)
            draw_scene_wo(offset)

            if t < SHOCK_MS:
                shock.fill((0, 0, 0, 0))
                prog = t / SHOCK_MS
                r = int(20 + prog * 140);
                a = max(0, int(180 * (1.0 - prog)))
                pygame.draw.circle(shock, (255, 255, 255, a), (int(cx + offset[0]), int(cy + offset[1])), r, 4)
                screen.blit(shock, (0, 0))

            for s in shards:
                if s.alpha <= 0: continue
                img = pygame.transform.rotozoom(s.surf, -s.angle, 1.0);
                img.set_alpha(s.alpha)
                screen.blit(img, (int(s.x + offset[0]), int(s.y + offset[1])))

            for sp in sparks:
                pygame.draw.circle(screen, sp.color, (int(sp.x + offset[0]), int(sp.y + offset[1])), sp.r)

            if t < FLASH_MS:
                flash.fill((255, 255, 255, int(220 * (1.0 - t / FLASH_MS))));
                screen.blit(flash, (0, 0))

            if is_fruit:
                screen.blit(target.surf, (int(target.x + offset[0]), int(fall_y + offset[1])))

            pygame.display.flip();
            clock.tick(FPS_LIMIT)
            if t > duration_ms: break
        return True

    def animate_hit(target):
        """Explosion + Death simultan da, wo sinnvoll (West & Ship)."""
        # --- Zombie (Ship, Atlas) ---
        if isinstance(target, Zombie):
            ship = levels[level_idx]
            # im Draw verstecken
            ship.hide_zombie = True
            # Explosion auf aktuellem Walk-Frame
            surf = ship.zombie.walk["frames"][target.dir][target.frame]
            death_frames = ship.zombie.death["frames"][target.dir]
            def draw_wo(offset):  # ohne Zombie rendern
                draw_base(offset)

            ok = animate_simul_explosion_death(
                screen, clock, draw_wo, death_frames, (int(target.x), int(target.y)), surf,
                override_color=(255, 40, 40),
                death_fps=get_death_fps_for(levels[level_idx].name, target)
            )

            # als erledigt markieren
            target.kill()
            target.dead_frame = len(death_frames)-1
            return ok

        # --- Normale Targets (West & Ship) ---
        is_west = levels[level_idx].name == "Wilder Westen"
        is_ship = levels[level_idx].name == "DeathShip"
        if (is_west or is_ship) and target.death_frames:
            # Standbild sofort ausblenden
            target.done = True
            def draw_wo(offset):
                draw_base(offset)
            # ggf. Balkon-Overlay nochmal OBEN drauf
            def overlay_top(offset):
                if is_west and hasattr(levels[level_idx], "draw_overlays"):
                    levels[level_idx].draw_overlays(screen, offset)

            ok = animate_simul_explosion_death(
                screen, clock, draw_wo, target.death_frames, (int(target.x), int(target.y)), target.surf,
                override_color=(255, 40, 40),
                death_fps=get_death_fps_for(levels[level_idx].name, target),
                overlay_top_fn=overlay_top
            )

            return ok

        # --- Baum (Frucht: Explosion+Fall) oder Targets ohne Deathframes ---
        def draw_wo(offset): draw_base(offset)
        # markiert intern target.done = True (kein Doppelbild)
        return animate_explosion(screen, clock, draw_wo, target, override_color=None)

    def advance_turn(hit, target_hit):
        nonlocal current_player_idx, active_players, round_hits, eliminated_set
        if hit and target_hit:
            if not animate_hit(target_hit): return False
            if hasattr(levels[level_idx], "update"): levels[level_idx].update(0)
            if levels[level_idx].all_down():
                goto_next_level()

        round_hits[current_player_idx] = bool(hit)
        current_player_idx += 1
        if current_player_idx < len(active_players): return True

        if len(active_players) > 2:
            if any(round_hits):
                new_active = [p for p,h in zip(active_players, round_hits) if h]
                eliminated_set.update(set(active_players)-set(new_active))
                active_players[:] = new_active
            round_hits[:] = [None]*len(active_players)
            current_player_idx=0
            return True

        if len(active_players)==2:
            a,b = round_hits
            if a and not b: eliminated_set.add(active_players[1]); show_winner(active_players[0]); return False
            if b and not a: eliminated_set.add(active_players[0]); show_winner(active_players[1]); return False
            round_hits[:] = [None,None]; current_player_idx=0; return True

        if len(active_players)==1:
            show_winner(active_players[0]); return False
        return True

    # ---------------- Loop ----------------
    running=True
    while running and hm_game_active():
        dt = clock.tick(FPS_LIMIT)/1000.0
        if hasattr(levels[level_idx], "update"): levels[level_idx].update(dt)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT or (ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE):
                running=False
            elif ev.type==pygame.KEYDOWN and ev.key==pygame.K_n:
                goto_next_level()
            elif ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=ev.pos
                hit,t=evaluate_shot(mx,my)
                hm_screenshot(screen)
                running=advance_turn(hit,t)

        if running and hm_hit_detected():
            pos=hm_get_pos()
            if pos:
                mx,my=pos; hit,t=evaluate_shot(mx,my)
                hm_screenshot(screen)
                running=advance_turn(hit,t)

        draw_scene_and_flip()

    pygame.quit()

if __name__=="__main__":
    main()
