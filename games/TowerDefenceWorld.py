import os, re, math, json, random, pygame

# ===== optionale HM-Systeme (fehler-tolerant) =================================
try:
    import hmsysteme
    HAS_HM = True
except Exception:
    HAS_HM = False

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

# ===== Basis / Performance =====================================================
WIDTH, HEIGHT = 1366, 768
FPS = 30
ASSET_ROOT = os.path.dirname(os.path.realpath(__file__))

# Explosion (rot), leichtgewichtig
EXP_DURATION = 0.9
GRAVITY = 1300.0
MAX_SHARDS = 24
SPARK_COUNT = 50
FLASH_MS = 100
SHAKE_MS = 180
SHAKE_AMPL = 10

# ===== Helpers =================================================================
def try_load(path):
    try: return pygame.image.load(path).convert_alpha()
    except Exception: return None

def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def load_json_relaxed(path):
    """Erlaubt //- und /**/-Kommentare + trailing commas."""
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"//.*?$", "", s, flags=re.M)
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return json.loads(s)

def _compute_anchors(frames_by_dir):
    """Fußpunkt-Anker = unterer Mittelpunkt des sichtbaren Bereichs (Frame 0)"""
    anchors = {}
    for d, frames in frames_by_dir.items():
        if not frames:
            anchors[d] = (0,0); continue
        img0 = frames[0]
        br = img0.get_bounding_rect(min_alpha=10)
        if br.w == 0 or br.h == 0:
            anchors[d] = (img0.get_width()//2, img0.get_height()-1)
        else:
            anchors[d] = (br.x + br.w//2, br.y + br.h - 1)
    return anchors

def load_grid_atlas(json_path, image_dir, fallbacks=()):
    """Grid-Atlas mit optional frame_width/-height, spacing(_x/_y), margin(_x/_y)."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    grid = data["grid"]; dirs = grid["dirs"]; fpd = int(grid["frames_per_dir"])
    meta = data.get("meta", {}) or {}
    imgname = meta.get("image") or ""
    candidates = [imgname]
    if imgname.endswith("x.png"):
        candidates.append(imgname[:-5] + ".png")
    candidates += list(fallbacks)

    sheet = None
    for c in candidates:
        if not c: continue
        p = os.path.join(image_dir, c)
        sheet = try_load(p)
        if sheet: break
    if sheet is None:
        raise FileNotFoundError(f"Spritesheet nicht gefunden (versucht: {candidates})")

    rows=len(dirs); cols=fpd
    fw = int(meta.get("frame_width") or 0)
    fh = int(meta.get("frame_height") or 0)
    sx = int(meta.get("spacing_x") or meta.get("spacing") or 0)
    sy = int(meta.get("spacing_y") or meta.get("spacing") or 0)
    mx = int(meta.get("margin_x")  or meta.get("margin")  or 0)
    my = int(meta.get("margin_y")  or meta.get("margin")  or 0)
    if fw <= 0 or fh <= 0:
        fw = sheet.get_width()  // cols
        fh = sheet.get_height() // rows
        sx = sy = mx = my = 0

    frames = {d: [] for d in dirs}
    masks  = {d: [] for d in dirs}
    for r,d in enumerate(dirs):
        for c in range(cols):
            x = mx + c * (fw + sx)
            y = my + r * (fh + sy)
            rect = pygame.Rect(x, y, fw, fh)
            rect.clamp_ip(pygame.Rect(0,0,sheet.get_width(),sheet.get_height()))
            img = sheet.subsurface(rect).copy()
            frames[d].append(img)
            masks[d].append(pygame.mask.from_surface(img))
    anchors = _compute_anchors(frames)
    return {"frames": frames, "masks": masks, "fw": fw, "fh": fh, "dirs": dirs, "anchors": anchors}

def scale_atlas(atlas, scale):
    if abs(scale-1.0) < 1e-3: return atlas
    for d in atlas["frames"]:
        new_frames=[]; new_masks=[]
        for img in atlas["frames"][d]:
            s = pygame.transform.smoothscale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            new_frames.append(s); new_masks.append(pygame.mask.from_surface(s))
        atlas["frames"][d] = new_frames
        atlas["masks"][d]  = new_masks
    atlas["anchors"] = {d: (int(ax*scale), int(ay*scale)) for d,(ax,ay) in atlas["anchors"].items()}
    atlas["fw"] = int(atlas["fw"]*scale); atlas["fh"] = int(atlas["fh"]*scale)
    return atlas

# ---- Pfade aus waves.json -----------------------------------------------------
def _normalize_paths_struct(obj):
    if not isinstance(obj, dict): return {}
    if "paths" in obj and isinstance(obj["paths"], list):
        out={}
        for i,arr in enumerate(obj["paths"]):
            if not isinstance(arr, list): continue
            pts=[tuple(map(float,p)) for p in arr]
            if len(pts)>=2: out[str(i)] = pts
        if out: return out
    if "paths" in obj and isinstance(obj["paths"], dict):
        out={}
        for name, arr in obj["paths"].items():
            if not isinstance(arr, list): continue
            pts=[tuple(map(float,p)) for p in arr]
            if len(pts)>=2: out[str(name)] = pts
        if out: return out
    if "feet" in obj and isinstance(obj["feet"], list):
        pts=[tuple(map(float,p)) for p in obj["feet"]]
        if len(pts)>=2: return {"0": pts}
    return {}

def _dedupe_close_points(pts, eps=0.5):
    if not pts: return pts
    out = [pts[0]]
    for x,y in pts[1:]:
        lx,ly = out[-1]
        if math.hypot(x-lx, y-ly) >= eps:
            out.append((x,y))
    return out

# ===== Explosion + Death =======================================================
class Shard:
    __slots__=("surf","x","y","vx","vy","angle","omega","alpha")
    def __init__(self,surf,x,y,vx,vy,angle,omega):
        self.surf=surf; self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.angle=angle; self.omega=omega; self.alpha=255

class Spark:
    __slots__=("x","y","vx","vy","life","r")
    def __init__(self,x,y,vx,vy,life,r):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy; self.life=life; self.r=r

class ExplosionEffect:
    def __init__(self, death_frames, feet_pos, surf_for_expl, death_anchor, death_fps=12):
        self.death_frames = death_frames
        self.feet = feet_pos
        self.death_anchor = death_anchor
        self.death_ms = max(1, int(1000 / max(1, death_fps)))
        self.start = pygame.time.get_ticks()
        self.tms = 0
        self.shards, self.sparks = self._make_pieces(surf_for_expl)

    def _make_pieces(self, surf):
        shards=[]; sparks=[]
        fw,fh = surf.get_width(), surf.get_height()
        tlx, tly = self.feet[0]-self.death_anchor[0], self.feet[1]-self.death_anchor[1]
        cx,cy = self.feet
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
                px = tlx+rx+br.x; py = tly+ry+br.y
                cands.append((piece,px,py))
        random.shuffle(cands)
        for piece,px,py in cands[:MAX_SHARDS]:
            ang=math.atan2(py-cy, px-cx)+random.uniform(-0.4,0.4)
            spd=random.uniform(420,820)
            vx=math.cos(ang)*spd; vy=math.sin(ang)*spd-random.uniform(140,260)
            shards.append(Shard(piece,px,py,vx,vy,random.uniform(0,360),random.uniform(-720,720)))
        for _ in range(SPARK_COUNT):
            ang=random.uniform(0,2*math.pi); spd=random.uniform(500,1000)
            vx=math.cos(ang)*spd; vy=math.sin(ang)*spd-random.uniform(80,180)
            life=random.uniform(0.18,0.42); r=random.randint(2,3)
            sparks.append(Spark(cx,cy,vx,vy,life,r))
        return shards,sparks

    def _shake(self, tms):
        if tms >= SHAKE_MS: return (0,0)
        k = 1.0 - (tms / SHAKE_MS)
        a = max(0, int(SHAKE_AMPL * k))
        return (random.randint(-a,a), random.randint(-a,a))

    def update(self, dt):
        now = pygame.time.get_ticks()
        self.tms = now - self.start
        for s in self.shards:
            s.vy += GRAVITY*dt; s.x += s.vx*dt; s.y += s.vy*dt; s.angle += s.omega*dt
            s.alpha = max(0, s.alpha - int(255*dt/EXP_DURATION))
        for sp in list(self.sparks):
            sp.life -= dt; sp.x += sp.vx*dt; sp.y += sp.vy*dt; sp.vx *= 0.985; sp.vy += GRAVITY*0.65*dt
            if sp.life <= 0: self.sparks.remove(sp)

    def draw(self, screen):
        off = self._shake(self.tms)
        if self.tms < 200:
            radius = int(16 + (self.tms/200.0)*140)
            alpha  = max(0, int(180*(1.0 - self.tms/200.0)))
            pygame.draw.circle(screen, (255,255,255,alpha),
                               (int(self.feet[0]+off[0]), int(self.feet[1]+off[1])), radius, 4)
        for s in self.shards:
            if s.alpha<=0: continue
            img=pygame.transform.rotozoom(s.surf,-s.angle,1.0); img.set_alpha(s.alpha)
            screen.blit(img,(int(s.x+off[0]), int(s.y+off[1])))
        for sp in self.sparks:
            pygame.draw.circle(screen, (255,60,60), (int(sp.x+off[0]), int(sp.y+off[1])), sp.r)
        if self.tms < FLASH_MS:
            a=int(210*(1.0-self.tms/FLASH_MS))
            f=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA); f.fill((255,255,255,a)); screen.blit(f,(0,0))
        idx = min(len(self.death_frames)-1, self.tms // self.death_ms)
        df  = self.death_frames[int(idx)]
        tlx = int(self.feet[0] - self.death_anchor[0] + off[0])
        tly = int(self.feet[1] - self.death_anchor[1] + off[1])
        screen.blit(df,(tlx,tly))

    def finished(self):
        return self.tms >= max(int(EXP_DURATION*1000), len(self.death_frames)*self.death_ms)

# ===== Gegner / Konfig ========================================================
def read_global_enemy_cfg():
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/Enemies/config.json")
    if os.path.isfile(p):
        try: return load_json_relaxed(p)
        except Exception as e: print("[WARN] Enemies/config.json fehlerhaft:", e)
    return {}

def read_gameplay_cfg():
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/gameplay.json")
    cfg = {"base_firepower": 1, "upgrade_threshold": 50, "upgrade_amount": 1, "max_firepower": 10}
    if os.path.isfile(p):
        try: cfg.update(load_json_relaxed(p))
        except Exception as e: print("[WARN] gameplay.json fehlerhaft:", e)
    return cfg

class EnemyType:
    """Lädt Walk/Death + Konfig (scale, move_speed, walk_fps, death_fps, hp, score)."""
    def __init__(self, name, folder, global_cfg):
        self.name = name
        base = name.lower()
        walk_json  = os.path.join(folder, f"{base}_walk.json")
        death_json = os.path.join(folder, f"{base}_death.json")
        self.walk  = load_grid_atlas(walk_json,  folder, fallbacks=("zWalk.png",))
        self.death = load_grid_atlas(death_json, folder, fallbacks=("zDeath.png",))

        local_cfg_path = os.path.join(folder, "config.json")
        cfg = {}
        if os.path.isfile(local_cfg_path):
            try: cfg = load_json_relaxed(local_cfg_path)
            except Exception as e: print(f"[WARN] {name}/config.json fehlerhaft: {e}")
        cfg = {**(global_cfg.get(name, {})), **cfg}

        self.scale      = float(cfg.get("scale", 1.0))
        self.speed      = float(cfg.get("move_speed", 95.0))
        self.walk_fps   = float(cfg.get("walk_fps", 10.0))
        self.death_fps  = int(cfg.get("death_fps", 12))
        self.hp         = int(cfg.get("hp", 3))
        self.score      = int(cfg.get("score", 10))
        self.headshot_top = float(cfg.get("headshot_top", 0.22))

        if abs(self.scale-1.0) > 1e-3:
            self.walk  = scale_atlas(self.walk,  self.scale)
            self.death = scale_atlas(self.death, self.scale)

        self.walk_anchor  = self.walk["anchors"]
        self.death_anchor = self.death["anchors"]

class Enemy:
    def __init__(self, etype: EnemyType, path_points, hp_override=None, hp_mul=None):
        self.etype = etype
        self.frames = etype.walk["frames"]; self.masks = etype.walk["masks"]
        self.death  = etype.death["frames"]
        self.walk_anchor = etype.walk_anchor
        self.death_anchor= etype.death_anchor

        base_hp = etype.hp
        if hp_mul is not None: base_hp = max(1, int(round(base_hp * float(hp_mul))))
        if hp_override is not None: base_hp = int(hp_override)
        self.hp = base_hp

        self.fx, self.fy = path_points[0]
        self.path = path_points; self.seg=0
        self.dir = "NE"; self.findex = 0
        self.anim_accum = 0.0
        self.dead=False

    def _dir_from_vec(self, dx,dy):
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
        if self.dead or self.seg >= len(self.path)-1: return
        v = self.etype.speed
        remain = v * dt
        snap_eps = 1.0
        while remain > 0 and self.seg < len(self.path)-1:
            tx, ty = self.path[self.seg+1]
            dx, dy = tx - self.fx, ty - self.fy
            dist = math.hypot(dx, dy)
            if dist <= snap_eps:
                self.fx, self.fy = tx, ty
                self.seg += 1
                continue
            self.dir = self._dir_from_vec(dx,dy)
            step = min(remain, dist)
            self.fx += (dx/dist) * step
            self.fy += (dy/dist) * step
            remain -= step

        self.anim_accum += dt
        step_anim = 1.0 / max(1e-6, self.etype.walk_fps)
        while self.anim_accum >= step_anim:
            self.anim_accum -= step_anim
            self.findex = (self.findex + 1) % len(self.frames[self.dir])

    def draw(self, screen):
        if self.dead: return
        frm = self.frames[self.dir][self.findex]
        ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax); tly = int(self.fy - ay)
        screen.blit(frm,(tlx,tly))

    def _local_hit_pos(self, mx,my):
        frm = self.frames[self.dir][self.findex]
        ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax); tly = int(self.fy - ay)
        rx,ry = mx - tlx, my - tly
        if 0 <= rx < frm.get_width() and 0 <= ry < frm.get_height():
            return (rx,ry)
        return None

    def hit_kind(self, mx, my, head_frac=None):
        """'head' / 'body' / 'none' – Maske + oberer Anteil des sichtbaren Bounds als Kopfzone."""
        # lokale Trefferkoordinate im aktuellen Frame
        frm = self.frames[self.dir][self.findex]
        ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax);
        tly = int(self.fy - ay)
        rx, ry = mx - tlx, my - tly
        if not (0 <= rx < frm.get_width() and 0 <= ry < frm.get_height()):
            return "none"

        m = self.masks[self.dir][self.findex]
        if not m.get_at((int(rx), int(ry))):
            return "none"

        # sichtbarer Bound
        brs = m.get_bounding_rects()
        br = brs[0] if brs else pygame.Rect(0, 0, *m.get_size())

        # Anteil aus Config (z.B. 0.25 bei TheSmith), fallback 0.22
        frac = head_frac if head_frac is not None else getattr(self.etype, "headshot_top", 0.22)
        frac = max(0.05, min(0.9, float(frac)))  # clamp

        head_h = max(1, int(br.h * frac))
        head_rect = pygame.Rect(br.x, br.y, br.w, head_h)
        return "head" if head_rect.collidepoint(rx, ry) else "body"

    def is_offscreen(self, margin=40):
        """Liegt die aktuelle Frame-Box komplett außerhalb des sichtbaren Bereichs?"""
        frm = self.frames[self.dir][self.findex]
        ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax);
        tly = int(self.fy - ay)
        w, h = frm.get_width(), frm.get_height()

        return (tlx + w < -margin or tlx > WIDTH + margin or
                tly + h < -margin or tly > HEIGHT + margin)

    def draw(self, screen):
        if self.dead:
            return
        frm = self.frames[self.dir][self.findex]
        ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax);
        tly = int(self.fy - ay)
        # quick-cull: gar nicht blitten, wenn außerhalb
        if (tlx + frm.get_width() < 0 or tlx > WIDTH or
                tly + frm.get_height() < 0 or tly > HEIGHT):
            return
        screen.blit(frm, (tlx, tly))

# ===== Level-Spezifikation (eine Datei: <Sublevel>.waves.json) =================
def load_level_spec(level_folder, subname, enemies_dict):
    def cand(name):
        return os.path.join(ASSET_ROOT,"pics/TowerDefence",level_folder,f"{name}.waves.json")
    path = None
    for nm in (subname,
               subname.lower().replace("burma","bruma").title() if "burma" in subname.lower() else subname,
               subname.lower().replace("bruma","burma").title() if "bruma" in subname.lower() else subname):
        p = cand(nm)
        if os.path.isfile(p): path = p; break
    # Fallback ohne waves.json: einfacher Brückenpfad, keine Auto-Spawns
    if not path:
        base = {"0":[(340,700),(900,170)]} if (level_folder.lower()=="level1" and subname.lower().startswith(("burma","bruma"))) \
               else {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}
        return base, []

    try:
        data = load_json_relaxed(path)
    except Exception as e:
        print("[WARN] waves.json fehlerhaft:", e)
        return {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}, []

    raw = _normalize_paths_struct(data) or {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}
    # dedupe nahe Punkte
    raw = {k:_dedupe_close_points(v, 0.5) for k,v in raw.items()}
    # case-insensitiv ablegen
    paths = {str(k).lower(): v for k,v in raw.items()}

    spawns = data.get("spawns") or []
    q=[]
    for s in spawns:
        if not isinstance(s, dict): continue
        typ = s.get("type","Zombie")
        if typ not in enemies_dict:
            print(f"[WARN] Unbekannter Gegnertyp '{typ}' in waves.")
            continue
        key = str(s.get("path","0")).lower()
        if key not in paths:
            print(f"[WARN] Spawn-Pfad '{s.get('path')}' nicht gefunden. Nutze ersten verfügbaren.")
            key = next(iter(paths.keys()))
        entry = {"t": float(s.get("t",0)), "type": typ, "path": key}
        if "hp" in s: entry["hp"] = int(s["hp"])
        if "hp_mul" in s: entry["hp_mul"] = float(s["hp_mul"])
        cnt = int(s.get("count",1)); iv=float(s.get("interval",0))
        for i in range(cnt):
            e2=dict(entry); e2["t"]=entry["t"]+i*iv; q.append(e2)
    q.sort(key=lambda x:x["t"])
    return paths, q

# ===== LevelState ==============================================================
class LevelState:
    def __init__(self, bg, paths_dict, enemy_types, gameplay_cfg, spawn_queue):
        self.bg = bg
        self.paths = paths_dict
        self.enemy_types = enemy_types
        self.enemies = []
        self.effects = []
        self.spawn_queue = list(spawn_queue)  # hier immer Liste
        self.time = 0.0

        # Firepower/Score
        self.firepower = int(gameplay_cfg.get("base_firepower",1))
        self.upgrade_threshold = int(gameplay_cfg.get("upgrade_threshold",50))
        self.upgrade_amount = int(gameplay_cfg.get("upgrade_amount",1))
        self.max_firepower = int(gameplay_cfg.get("max_firepower",10))
        self.score = 0
        self.next_upgrade_at = self.upgrade_threshold

        self.font_small = pygame.font.SysFont(None, 24)

    def _maybe_upgrade(self):
        while self.score >= self.next_upgrade_at and self.firepower < self.max_firepower:
            self.firepower += self.upgrade_amount
            self.next_upgrade_at += self.upgrade_threshold

    def apply_hit(self, mx, my):
        """Maus/HM-Treffer anwenden (mit Headshot für 'TheSmith')."""
        for e in reversed(self.enemies):
            if e.dead:
                continue

            kind = e.hit_kind(mx, my)  # nutzt jetzt etype.headshot_top
            if kind == "none":
                continue

            # Spezielle Boss-Regel
            if e.etype.name.lower() == "thesmith" and kind == "head":
                e.hp = 0  # Sofort-KO
            else:
                e.hp -= max(1, self.firepower)

            if e.hp <= 0:
                frm = e.frames[e.dir][e.findex]
                self.effects.append(ExplosionEffect(
                    e.death[e.dir],
                    (int(e.fx), int(e.fy)),
                    frm,
                    e.death_anchor[e.dir],
                    death_fps=e.etype.death_fps
                ))
                e.dead = True
                self.score += e.etype.score
                self._maybe_upgrade()
            return True  # ein Ziel pro Klick bearbeiten

        return False

    def update_spawning(self, dt):
        # präzise Waves
        self.time += dt
        while self.spawn_queue and self.spawn_queue[0]["t"] <= self.time:
            s = self.spawn_queue.pop(0)
            path_pts = self.paths.get(s["path"]) or next(iter(self.paths.values()))
            self.enemies.append(Enemy(
                self.enemy_types[s["type"]], path_pts,
                hp_override=s.get("hp"), hp_mul=s.get("hp_mul")
            ))

    def draw_hud(self, screen):
        # Firepower oben rechts
        text = self.font_small.render(f"Firepower: {self.firepower}", True, (255,255,255))
        screen.blit(text, (WIDTH - text.get_width() - 10, 8))

# ===== MAIN ===================================================================
def main():
    pygame.init()
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1)
    except TypeError:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("TowerDefence — Minimal")
    clock = pygame.time.Clock()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    # Gegner laden (lokale Typ-Configs inkl. Kommentare sind erlaubt)
    ENEMY_TYPES = {}
    enemies_root = os.path.join(ASSET_ROOT, "pics/TowerDefence/Enemies")
    global_cfg = read_global_enemy_cfg()
    for name in os.listdir(enemies_root):
        folder = os.path.join(enemies_root, name)
        if os.path.isdir(folder):
            try:
                ENEMY_TYPES[name] = EnemyType(name, folder, global_cfg)
            except Exception as e:
                print(f"[WARN] Gegner {name} konnte nicht geladen werden:", e)
    if not ENEMY_TYPES:
        raise SystemExit("Keine Gegner in pics/TowerDefence/Enemies/ gefunden.")
    gameplay_cfg = read_gameplay_cfg()

    # Level/Sublevel finden
    def discover_sublevels(level_folder):
        p = os.path.join(ASSET_ROOT, "pics/TowerDefence", level_folder)
        if not os.path.isdir(p): return []
        imgs = [f for f in os.listdir(p) if f.lower().endswith(".png")]
        imgs.sort(key=natural_key)
        return [(os.path.splitext(f)[0], os.path.join(p, f)) for f in imgs]

    levels = [f"Level{i}" for i in range(1,51) if discover_sublevels(f"Level{i}")]
    if not levels: raise SystemExit("Keine Levelordner mit PNGs gefunden.")
    level_index = 0
    sublevels = discover_sublevels(levels[level_index])
    sub_index = 0

    def build_state(level_folder, subname, img_path):
        bg = try_load(img_path)
        if bg is None:
            bg = pygame.Surface((WIDTH, HEIGHT)); bg.fill((40,60,40))
        else:
            bg = pygame.transform.smoothscale(bg,(WIDTH,HEIGHT))
        paths_dict, spawn_q = load_level_spec(level_folder, subname, ENEMY_TYPES)
        return LevelState(bg, paths_dict, ENEMY_TYPES, gameplay_cfg, spawn_q)

    subname, img_path = sublevels[sub_index]
    state = build_state(levels[level_index], subname, img_path)

    # Fadenkreuz (klein)
    cross = pygame.Surface((22,22), pygame.SRCALPHA)
    pygame.draw.circle(cross,(255,255,255),(11,11),10,1)
    pygame.draw.line(cross,(255,255,255),(0,11),(22,11),1)
    pygame.draw.line(cross,(255,255,255),(11,0),(11,22),1)
    cross_pos=None; cross_until=0

    running=True
    while running and hm_game_active():
        dt = clock.tick(FPS)/1000.0

        state.update_spawning(dt)
        for e in state.enemies: e.update(dt)
        # Gegner, die tot sind ODER ihr Ziel erreicht haben und off-screen sind, entfernen
        pruned = []
        for e in state.enemies:
            if e.dead:
                continue
            # nur nach dem letzten Segment despawnen (damit Start außerhalb des Bildes OK ist)
            if e.seg >= len(e.path) - 1 and e.is_offscreen(margin=48):
                continue
            pruned.append(e)
        state.enemies = pruned

        for eff in list(state.effects):
            eff.update(dt)
            if eff.finished(): state.effects.remove(eff)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT or (ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE):
                running=False
            elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx,my = ev.pos
                cross_pos = (mx - cross.get_width()//2, my - cross.get_height()//2)
                cross_until = pygame.time.get_ticks() + 120
                state.apply_hit(mx,my)

        if hm_hit_detected():
            pos = hm_get_pos()
            if pos:
                mx,my = pos
                cross_pos = (mx - cross.get_width()//2, my - cross.get_height()//2)
                cross_until = pygame.time.get_ticks() + 120
                state.apply_hit(mx,my)

        # Sublevel-Fortschritt: weiter, wenn alle geplanten Spawns draußen UND alles tot/abgelaufen
        alive = [e for e in state.enemies if not e.dead]
        if not state.spawn_queue and not alive and not state.effects:
            sub_index += 1
            if sub_index >= len(sublevels):
                level_index += 1
                if level_index >= len(levels): break
                sublevels = discover_sublevels(levels[level_index]); sub_index = 0
            subname, img_path = sublevels[sub_index]
            state = build_state(levels[level_index], subname, img_path)

        # Render
        screen.blit(state.bg,(0,0))
        for e in state.enemies: e.draw(screen)
        for eff in state.effects: eff.draw(screen)
        state.draw_hud(screen)
        if cross_pos and pygame.time.get_ticks() < cross_until:
            screen.blit(cross, (int(cross_pos[0]), int(cross_pos[1])))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
