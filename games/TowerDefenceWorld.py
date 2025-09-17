import os, re, math, json, random, pygame

# ===== HM-Systeme (optional) ==================================================
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
SPARK_COUNT = 38
FLASH_MS = 100
SHAKE_MS = 180
SHAKE_AMPL = 10

# Overlays
OVERLAY_BLOCK_ALPHA = 20  # ab welcher Alpha ein Overlay Klicks blockt (0..255)

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
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)       # Blockkommentare
    s = re.sub(r"//.*?$", "", s, flags=re.M)          # Zeilenkommentare
    s = re.sub(r",\s*([}\]])", r"\1", s)              # trailing commas
    return json.loads(s)

def _compute_anchors(frames_by_dir):
    """Fußpunkt-Anker = unterer Mittelpunkt des sichtbaren Bereichs (Frame 0)."""
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

def atlas_from_sheet_like_walk(sheet, walk_atlas):
    """Fallback: baue 'hit'-Atlas aus hit.png mit den Maßen des walk-Atlas."""
    fw, fh = walk_atlas["fw"], walk_atlas["fh"]
    dirs = walk_atlas["dirs"]
    fpd  = len(next(iter(walk_atlas["frames"].values())))
    sheet_w, sheet_h = sheet.get_width(), sheet.get_height()
    rows = len(dirs)
    cols = max(1, min(fpd, sheet_w // max(1, fw)))
    frames={d:[] for d in dirs}; masks={d:[] for d in dirs}
    for r, d in enumerate(dirs[:rows]):
        for c in range(cols):
            x = c*fw; y = r*fh
            if x+fw>sheet_w or y+fh>sheet_h: break
            img = sheet.subsurface(pygame.Rect(x,y,fw,fh)).copy()
            frames[d].append(img)
            masks[d].append(pygame.mask.from_surface(img))
    anchors = _compute_anchors(frames)
    return {"frames":frames,"masks":masks,"fw":fw,"fh":fh,"dirs":dirs,"anchors":anchors}

# ---- Pfade/Waves aus waves.json ----------------------------------------------
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

# ===== Text mit Outline ========================================================
def blit_text_outline(screen, font, text, pos, color=(255,255,255), outline=(0,0,0), w=2, align_right=True):
    base = font.render(text, True, color)
    bx, by = pos
    def place(surf, dx, dy):
        r = surf.get_rect()
        if align_right: r.topright = (bx+dx, by+dy)
        else:           r.topleft  = (bx+dx, by+dy)
        screen.blit(surf, r)
    if w > 0:
        out = font.render(text, True, outline)
        for dx in range(-w, w+1):
            for dy in range(-w, w+1):
                if dx == 0 and dy == 0: continue
                place(out, dx, dy)
    place(base, 0, 0)

def wrap_lines(font, text, max_width):
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        if font.size(test)[0] <= max_width or not line:
            line.append(w)
        else:
            lines.append(" ".join(line))
            line = [w]
    if line:
        lines.append(" ".join(line))
    return lines

# ===== Floating score text =====================================================
class FloatingText:
    __slots__=("x","y","t","dur","rise","surf","shadow")
    def __init__(self, text, x, y, font, color=(120,255,120), duration=1.5, rise=60):
        self.x, self.y = float(x), float(y)
        self.t, self.dur, self.rise = 0.0, float(duration), float(rise)
        self.surf   = font.render(text, True, color)
        self.shadow = font.render(text, True, (0,0,0))
    def update(self, dt):
        self.t += dt; self.y -= self.rise * dt
    def draw(self, screen):
        a = max(0, min(255, int(255 * (1.0 - self.t / self.dur))))
        self.shadow.set_alpha(a); self.surf.set_alpha(a)
        screen.blit(self.shadow, (int(self.x)+1, int(self.y)+1))
        screen.blit(self.surf,   (int(self.x),   int(self.y)))
    def finished(self): return self.t >= self.dur

# ===== Power-up Effekt =========================================================
class PowerUpEffect:
    def __init__(self, msg="Firepower +1!", duration=1.8):
        self.msg = msg; self.t = 0.0; self.dur = float(duration)
    def update(self, dt): self.t += dt
    def draw(self, screen, font_big):
        if self.t >= self.dur: return
        k = self.t / self.dur
        cx = WIDTH // 2; cy = HEIGHT // 2
        r = int(80 + 120 * (1.0 - k))
        alpha = max(0, int(140 * (1.0 - k)))
        glow = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 120, alpha), (r+1, r+1), r, 8)
        screen.blit(glow, (cx - r, cy - r))
        scale = 1.15 + 0.25 * math.sin(k * math.pi)
        text = font_big.render(self.msg, True, (255, 255, 180))
        text = pygame.transform.rotozoom(text, 0, scale)
        tx = cx - text.get_width() // 2; ty = cy - text.get_height() // 2
        shadow = font_big.render(self.msg, True, (0,0,0))
        shadow = pygame.transform.rotozoom(shadow, 0, scale)
        screen.blit(shadow, (tx+3, ty+3)); screen.blit(text, (tx, ty))
    def finished(self): return self.t >= self.dur

# ===== Explosion ===============================================================
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
            spd=random.uniform(380,720)
            vx=math.cos(ang)*spd; vy=math.sin(ang)*spd-random.uniform(120,220)
            shards.append(Shard(piece,px,py,vx,vy,random.uniform(0,360),random.uniform(-720,720)))
        for _ in range(SPARK_COUNT):
            ang=random.uniform(0,2*math.pi); spd=random.uniform(420,820)
            vx=math.cos(ang)*spd; vy=math.sin(ang)*spd-random.uniform(60,160)
            life=random.uniform(0.22,0.45); r=random.randint(2,3)
            sparks.append(Spark(cx,cy,vx,vy,life,r))
        return shards,sparks
    def _shake(self, tms):
        if tms >= SHAKE_MS: return (0,0)
        k = 1.0 - (tms / SHAKE_MS)
        a = max(0, int(SHAKE_AMPL * k))
        return (random.randint(-a,a), random.randint(-a,a))
    def update(self, dt):
        now = pygame.time.get_ticks(); self.tms = now - self.start
        for s in self.shards:
            s.vy += GRAVITY*dt; s.x += s.vx*dt; s.y += s.vy*dt; s.angle += s.omega*dt
            s.alpha = max(0, s.alpha - int(255*dt/EXP_DURATION))
        for sp in list(self.sparks):
            sp.life -= dt; sp.x += sp.vx*dt; sp.y += sp.vy*dt; sp.vx *= 0.985; sp.vy += GRAVITY*0.65*dt
            if sp.life <= 0: self.sparks.remove(sp)
    def draw(self, screen):
        off = self._shake(self.tms)
        if self.tms < 200:
            ring = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            radius = int(16 + (self.tms/200.0)*140)
            alpha  = max(0, int(160*(1.0 - self.tms/200.0)))
            pygame.draw.circle(ring, (255,255,255,alpha),
                               (int(self.feet[0]+off[0]), int(self.feet[1]+off[1])), radius, 4)
            screen.blit(ring,(0,0))
        for s in self.shards:
            if s.alpha<=0: continue
            img=pygame.transform.rotozoom(s.surf,-s.angle,1.0); img.set_alpha(s.alpha)
            screen.blit(img,(int(s.x+off[0]), int(s.y+off[1])))
        for sp in self.sparks:
            if sp.life <= 0: continue
            pygame.draw.circle(screen, (255,60,60), (int(sp.x+off[0]), int(sp.y+off[1])), sp.r)
        if self.tms < FLASH_MS:
            a=int(210*(1.0-self.tms/FLASH_MS))
            f=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            f.fill((255,255,255,a)); screen.blit(f,(0,0))
        idx = min(len(self.death_frames)-1, self.tms // self.death_ms)
        df  = self.death_frames[int(idx)]
        tlx = int(self.feet[0] - self.death_anchor[0] + off[0])
        tly = int(self.feet[1] - self.death_anchor[1] + off[1])
        screen.blit(df,(tlx,tly))
    def finished(self):
        return self.tms >= max(int(EXP_DURATION*1000), len(self.death_frames)*self.death_ms)

class HitPopEffect:
    """Leichte Treffer-Explosion (Ring + Funken), ohne Shards/Death-Frames."""
    def __init__(self, feet_pos, duration=0.35, spark_count=18):
        self.feet = (int(feet_pos[0]), int(feet_pos[1]))
        self.dur = float(duration)
        self.t = 0.0
        self.sparks = []
        cx, cy = self.feet
        for _ in range(spark_count):
            ang = random.uniform(0, 2*math.pi)
            spd = random.uniform(380, 700)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd - random.uniform(60, 160)
            life = random.uniform(0.18, 0.32)
            r = random.randint(2, 3)
            self.sparks.append(Spark(cx, cy, vx, vy, life, r))

    def update(self, dt):
        self.t += dt
        for sp in list(self.sparks):
            sp.life -= dt
            sp.x += sp.vx * dt
            sp.y += sp.vy * dt
            sp.vx *= 0.985
            sp.vy += GRAVITY * 0.55 * dt
            if sp.life <= 0:
                self.sparks.remove(sp)

    def draw(self, screen):
        # kurzer Ring-Flash am Anfang
        if self.t <= 0.18:
            k = self.t / 0.18
            radius = int(12 + 90 * k)
            alpha = max(0, int(160 * (1.0 - k)))
            ring = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(ring, (255, 255, 255, alpha), self.feet, radius, 3)
            screen.blit(ring, (0, 0))
        # Funken
        for sp in self.sparks:
            if sp.life > 0:
                pygame.draw.circle(screen, (255, 60, 60), (int(sp.x), int(sp.y)), sp.r)

    def finished(self):
        return self.t >= self.dur and not self.sparks


# ===== Lightweight BossProp (statischer Boss + kurze Attack-Animation) =====
# ===== Lightweight BossProp (statischer Boss + kurze Attack-Animation) =====
class BossProp:
    def __init__(self, frames_south, anchor_south, feet_pos, fps=10, scale=1.0):
        self.frames = [f.convert_alpha() for f in frames_south]
        self.anchor = anchor_south
        # Einmalige Skalierung
        if abs(scale - 1.0) > 1e-3:
            scaled = []
            for img in self.frames:
                w = int(img.get_width() * scale)
                h = int(img.get_height() * scale)
                scaled.append(pygame.transform.smoothscale(img, (w, h)))
            self.frames = scaled
            self.anchor = (int(self.anchor[0] * scale), int(self.anchor[1] * scale))

        self.fx, self.fy = float(feet_pos[0]), float(feet_pos[1])
        self.idx = 0
        self.playing = False
        self.fps = float(fps)
        self.t = 0.0
        self.play_t_remain = 0.0  # für play_for()

    def set_feet(self, feet_pos):
        self.fx, self.fy = float(feet_pos[0]), float(feet_pos[1])

    # kurze Attack-Animation (einmal durchlaufen)
    def play(self, seconds=None):
        self.playing = True
        self.t = 0.0
        if seconds is None:
            seconds = max(0.7, len(self.frames) / max(1.0, self.fps))
        self.play_t_remain = float(seconds)
        return self.play_t_remain

    # kompatibel zu LevelState.trigger_attack_shout()
    def play_for(self, seconds):
        return self.play(seconds)

    def update(self, dt):
        if not self.playing:
            return
        self.t += dt
        self.play_t_remain -= dt
        # Frame-Advance
        fcount = max(1, len(self.frames))
        self.idx = min(fcount - 1, int(self.t * self.fps))
        if self.play_t_remain <= 0.0:
            self.playing = False
            self.idx = 0

    def draw(self, screen):
        img = self.frames[self.idx if self.playing else 0]
        ax, ay = self.anchor
        tlx = int(self.fx - ax)
        tly = int(self.fy - ay)
        screen.blit(img, (tlx, tly))

# ===== Gegner / Konfig ========================================================
def read_global_enemy_cfg():
    """Optional: globale Defaults für fps/headshot_top (keine HP/Score/Speed/Scale)."""
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/Enemies/config.json")
    if os.path.isfile(p):
        try: return load_json_relaxed(p)
        except Exception as e: print("[WARN] Enemies/config.json fehlerhaft:", e)
    return {}

def read_gameplay_cfg():
    """Spielweite Defaults & Upgrades (nur Fallbacks für Level)."""
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/gameplay.json")
    cfg = {
        "base_firepower": 1,
        "upgrade_threshold": 50,
        "upgrade_amount": 1,
        "max_firepower": 10,
        "default_hp": 3,
        "default_score": 10,
        "default_headshot_mul": 2.0,
        "default_speed": 95.0,
        "default_scale": 1.0
    }
    if os.path.isfile(p):
        try: cfg.update(load_json_relaxed(p))
        except Exception as e: print("[WARN] gameplay.json fehlerhaft:", e)
    return cfg

# ===== WORLDS LAYER ============================================================
def discover_worlds():
    """Findet Welten in pics/TowerDefence/Worlds/<World>"""
    root = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds")
    worlds = []
    if os.path.isdir(root):
        for w in sorted(os.listdir(root)):
            if os.path.isdir(os.path.join(root, w)):
                worlds.append(w)
    return worlds

def world_full_image(world):
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds", world, f"{world}_full.png")
    return try_load(p)

def discover_levels(world):
    """Gibt Levelordner zurück (Level1, Level2, ...) die PNG-Sublevel enthalten."""
    base = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds", world)
    levels = []
    if not os.path.isdir(base): return levels
    for name in sorted(os.listdir(base), key=natural_key):
        p = os.path.join(base, name)
        if not os.path.isdir(p): continue
        imgs = [f for f in os.listdir(p) if f.lower().endswith(".png") and not f.lower().startswith("overlay") and "_full" not in f.lower()]
        if imgs:
            levels.append(name)
    return levels

def discover_sublevels(world, level_folder):
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds", world, level_folder)
    if not os.path.isdir(p): return []
    imgs = []
    for f in os.listdir(p):
        lf = f.lower()
        if not lf.endswith(".png"): continue
        if lf.startswith("overlay") or ".overlay" in lf: continue
        if "_full" in lf: continue
        imgs.append(f)
    imgs.sort(key=natural_key)
    return [(os.path.splitext(f)[0], os.path.join(p, f)) for f in imgs]

# ===== Level/Waves: Pfade, Spawns, Overlay-Regeln =============================
def load_level_spec(world, level_folder, subname, enemies_dict):
    """Liest <Sublevel>.waves.json und liefert (paths, waves, overlay_rules, mods).
       - Unterstützt {waves:[{label,require_enter,mods,spawns:[...]},...]}
       - Fällt zurück auf {spawns:[...]} als eine einzige Welle."""
    def cand(name):
        base = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds", world, level_folder)
        return os.path.join(base, f"{name}.waves.json")
    path = None
    for nm in (subname,
               subname.lower().replace("burma","bruma").title() if "burma" in subname.lower() else subname,
               subname.lower().replace("bruma","burma").title() if "bruma" in subname.lower() else subname):
        p = cand(nm)
        if os.path.isfile(p): path = p; break

    if not path:
        base = {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}
        return base, [], [], {}

    try:
        data = load_json_relaxed(path)
    except Exception as e:
        print("[WARN] waves.json fehlerhaft:", e)
        return {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}, [], [], {}

    raw = _normalize_paths_struct(data) or {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}
    raw = {k:_dedupe_close_points(v, 0.5) for k,v in raw.items()}
    paths = {str(k).lower(): v for k,v in raw.items()}

    def normalize_spawns(spawns):
        q=[]
        for s in spawns or []:
            if not isinstance(s, dict): continue
            typ = s.get("type","Zombie")
            if typ not in enemies_dict:
                print(f"[WARN] Unbekannter Gegnertyp '{typ}' in waves."); continue
            key = str(s.get("path","0")).lower()
            if key not in paths:
                print(f"[WARN] Spawn-Pfad '{s.get('path')}' nicht gefunden. Nutze ersten verfügbaren.")
                key = next(iter(paths.keys()))
            base = {"t": float(s.get("t",0)), "type": typ, "path": key}
            if "id" in s: base["id"] = str(s["id"])
            # optionale Felder inkl. Aura
            for fld in ("hp","hp_mul","score","score_mul","headshot_mul","headshot_instant_kill","move_speed","scale","aura"):
                if fld in s: base[fld] = s[fld]
            # count/interval-Expansion
            cnt = int(s.get("count",1)); iv = float(s.get("interval",0))
            for i in range(cnt):
                e2 = dict(base); e2["t"] = base["t"] + i*iv; q.append(e2)
        q.sort(key=lambda x:x["t"]); return q

    waves=[]
    if isinstance(data.get("waves"), list) and data["waves"]:
        for w in data["waves"]:
            waves.append({
                "label": w.get("label",""),
                "require_enter": bool(w.get("require_enter", False)),
                "mods": w.get("mods") or {},
                "spawns": normalize_spawns(w.get("spawns"))
            })
    else:
        waves.append({
            "label": data.get("title",""),
            "require_enter": True,
            "mods": {},
            "spawns": normalize_spawns(data.get("spawns") or [])
        })

    # Overlays (wie bisher)
    overlay_rules = []
    for o in data.get("overlays", []):
        if not isinstance(o, dict): continue
        fname = o.get("file")
        if not fname: continue
        rule = {"file": fname, "active": bool(o.get("active", True)), "blocks": bool(o.get("blocks", True))}
        act = o.get("activate_at")
        if isinstance(act, dict) and "x" in act and "y" in act:
            rule["activate_at"] = {"x": float(act["x"]), "y": float(act["y"]), "radius": float(act.get("radius", 24))}
            rule["active"] = False
        elif isinstance(act, (list, tuple)) and len(act) >= 2:
            rule["activate_at"] = {"x": float(act[0]), "y": float(act[1]), "radius": float(o.get("radius", 24))}
            rule["active"] = False
        if "only_type" in o: rule["only_type"] = str(o["only_type"])
        if "only_spawn_id" in o: rule["only_spawn_id"] = str(o["only_spawn_id"])
        overlay_rules.append(rule)

    # --- am Ende von load_level_spec(...) vor dem return ---
    level_mods = data.get("mods") or {}

    # Boss-Konfig separat ablegen (für LevelState.attach_boss_from_level_cfg)
    if isinstance(data.get("boss"), dict):
        level_mods["__boss_cfg__"] = dict(data["boss"])

    # Boss-Intro (Bild links / Text rechts)
    if isinstance(data.get("boss_intro"), dict):
        bi = data["boss_intro"]
        level_mods["__boss_intro__"] = {
            "show": bool(bi.get("show", True)),
            "text": str(bi.get("text") or ""),
            "bg_alpha": int(bi.get("bg_alpha", 200)),
        }

    return paths, waves, overlay_rules, level_mods


# ===== Overlays laden (mit Regeln) ============================================
def load_overlays(world, level_folder, subname, overlay_rules):
    """Sucht overlay*.png/<subname>.overlay*.png und verheiratet sie mit overlay_rules."""
    folder = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds", world, level_folder)
    if not os.path.isdir(folder): return []

    files = sorted(os.listdir(folder))
    found = []
    sub_low = subname.lower()
    for f in files:
        lf = f.lower()
        if lf.endswith(".png") and (lf.startswith("overlay") or ".overlay" in lf):
            found.append(f)

    overlays=[]
    rmap = {r["file"].lower(): r for r in overlay_rules}
    for f in found:
        p = os.path.join(folder, f)
        img = try_load(p)
        if not img: continue
        if img.get_size() != (WIDTH, HEIGHT):
            img = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
        rule = rmap.get(f.lower()) or rmap.get((sub_low + "." + f).lower())
        if rule:
            trigger = rule.get("activate_at")
            tr = {"x": trigger["x"], "y": trigger["y"], "r": trigger["radius"]} if trigger else None
            overlays.append({"surf": img, "active": bool(rule.get("active", True)),
                             "blocks": bool(rule.get("blocks", True)), "trigger": tr,
                             "only_type": rule.get("only_type"), "only_spawn_id": rule.get("only_spawn_id")})
        else:
            overlays.append({"surf": img, "active": True, "blocks": True, "trigger": None,
                             "only_type": None, "only_spawn_id": None})
    return overlays

# ===== Titel-Helfer ============================================================
def get_level_title(world, level_folder, subname):
    """Liest optional "title" aus <Sublevel>.waves.json.
    Fallback: "<LevelOrdner> — <SublevelName>"."""
    try:
        base = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds", world, level_folder)
        path = os.path.join(base, f"{subname}.waves.json")
        if os.path.isfile(path):
            data = load_json_relaxed(path)
            t = data.get("title")
            if isinstance(t, str) and t.strip():
                return t.strip()
    except Exception:
        pass
    # Default
    return f"{level_folder} — {subname}"

# ===== Level-Ende Overlay ======================================================
class LevelEndOverlay:
    def __init__(self, stats, next_label):
        self.stats = stats; self.next_label = next_label
    def draw(self, screen, font_big, font_hud):
        overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,160)); screen.blit(overlay,(0,0))
        title = font_big.render("Level beendet", True, (220,255,220))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 170))
        lines = [
            f"Firepower: {self.stats['firepower']}",
            f"Score: {self.stats['score']}",
            f"Erledigt: {self.stats['kills']}",
            f"Durchgelassen: {self.stats['escapes']}/{self.stats['max_escapes']}"
        ]
        y = HEIGHT//2 - 80
        for s in lines:
            txt = font_hud.render(s, True, (235,235,235))
            sh  = font_hud.render(s, True, (0,0,0))
            screen.blit(sh,  (WIDTH//2 - sh.get_width()//2 + 2, y + 2))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
            y += txt.get_height() + 10
        nxt = font_hud.render(f"Weiter zu: {self.next_label}", True, (255,255,200))
        screen.blit(nxt, (WIDTH//2 - nxt.get_width()//2, y + 16))
        hint = font_hud.render("Drücke ENTER, um fortzufahren", True, (255,255,255))
        sh   = font_hud.render("Drücke ENTER, um fortzufahren", True, (0,0,0))
        screen.blit(sh,   (WIDTH//2 - sh.get_width()//2 + 2, y + 50 + 2))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2,    y + 50))
# ===== Gegner-Klassen ==========================================================
class EnemyType:
    """Lädt Walk/Death (+ optional Hit). FPS/Kopfzone aus config.json.
       Scale/Speed kommen pro Level/Spawn aus waves.json."""
    def __init__(self, name, folder, global_cfg):
        self.name = name
        base = name.lower()
        walk_json  = os.path.join(folder, f"{base}_walk.json")
        death_json = os.path.join(folder, f"{base}_death.json")
        self.walk  = load_grid_atlas(walk_json,  folder, fallbacks=("zWalk.png",))
        self.death = load_grid_atlas(death_json, folder, fallbacks=("zDeath.png",))

        # Optional: Hit-Animation
        self.hit = None
        hit_json = os.path.join(folder, f"{base}_hit.json")
        try_img = os.path.join(folder, "hit.png")
        if os.path.isfile(hit_json):
            try:
                self.hit = load_grid_atlas(hit_json, folder, fallbacks=("hit.png",))
            except Exception as e:
                print(f"[WARN] {name}: hit-json konnte nicht geladen werden: {e}")
        elif os.path.isfile(try_img):
            sheet = try_load(try_img)
            if sheet:
                self.hit = atlas_from_sheet_like_walk(sheet, self.walk)

        # Lokale/Globale Konfigs (nur fps + Kopfzone)
        cfg = {}
        local_cfg_path = os.path.join(folder, "config.json")
        if os.path.isfile(local_cfg_path):
            try: cfg = load_json_relaxed(local_cfg_path)
            except Exception as e: print(f"[WARN] {name}/config.json fehlerhaft: {e}")
        cfg = {**(global_cfg.get(name, {})), **cfg}
        # komplette, zusammengeführte Gegner-Config für spätere Features merken
        self.cfg_full = dict(cfg)

        self.walk_fps     = float(cfg.get("walk_fps", 10.0))
        self.hit_fps      = float(cfg.get("hit_fps", 10.0))
        self.death_fps    = int(cfg.get("death_fps", 12))
        self.headshot_top = float(cfg.get("headshot_top", 0.22))

        # Skalierungs-Cache
        self._scaled_cache = {1.0: {"walk": self.walk, "death": self.death, "hit": self.hit}}

    def _clone_atlas(self, a):
        return {
            "frames": {d: list(fr) for d,fr in a["frames"].items()},
            "masks":  {d: list(ms) for d,ms in a["masks"].items()},
            "fw": a["fw"], "fh": a["fh"], "dirs": list(a["dirs"]),
            "anchors": dict(a["anchors"])
        }

    def get_scaled(self, scale: float):
        key = round(float(scale), 3)
        if key in self._scaled_cache:
            return self._scaled_cache[key]
        w = self._clone_atlas(self.walk);  w = scale_atlas(w, key)
        d = self._clone_atlas(self.death); d = scale_atlas(d, key)
        h = None
        if self.hit:
            h = self._clone_atlas(self.hit); h = scale_atlas(h, key)
        self._scaled_cache[key] = {"walk": w, "death": d, "hit": h}
        return self._scaled_cache[key]

class Enemy:
    def __init__(self, etype: EnemyType, path_points,
                 hp, score,
                 headshot_mul=2.0, headshot_instant_kill=False,
                 speed=95.0, scale=1.0, aura=None):
        self.etype = etype
        scaled = etype.get_scaled(scale)
        self.frames = scaled["walk"]["frames"]
        self.masks  = scaled["walk"]["masks"]
        self.death  = scaled["death"]["frames"]
        self.hit_frames = scaled["hit"]["frames"] if scaled["hit"] else None
        self.walk_anchor  = scaled["walk"]["anchors"]
        self.death_anchor = scaled["death"]["anchors"]
        self.hit_anchor   = scaled["hit"]["anchors"] if scaled["hit"] else None
        self._init_aura(aura)

        self.speed = float(speed)
        self.hp = int(hp)
        self.score = int(score)
        self.headshot_mul = float(headshot_mul)
        self.headshot_instant_kill = bool(headshot_instant_kill)

        self.fx, self.fy = path_points[0]
        self.path = path_points; self.seg=0
        self.dir="NE"; self.findex=0; self.anim_accum=0.0
        self.dead=False
        self.hit_active=False; self.hit_index=0; self.hit_anim_accum=0.0
        self.spawn_id=None

        # ---- Aura (optional, lazy-precompute pro Frame)
        self.aura = None
        if isinstance(aura, dict):
            try:
                rad = int(max(1, min(16, int(aura.get("radius", 0)))))
                col = aura.get("color", [255, 215, 0, 150])
                r, g, b, a = int(col[0]), int(col[1]), int(col[2]), int(col[3])
                self.aura = {
                    "radius": rad,
                    "rgb": (r, g, b),
                    "alpha": int(max(0, min(255, a))),
                    "layers": {d: [None] * len(self.frames[d]) for d in self.frames},
                    "t": 0.0,
                    "freq": 0.5,  # Puls-Frequenz (Hz)
                }
            except Exception:
                self.aura = None

    def _init_aura(self, cfg):
        """cfg = {"radius":8,"color":[r,g,b,a], "freq":0.8}"""
        self.aura = None
        if not isinstance(cfg, dict):
            return
        try:
            rad = int(max(1, min(16, int(cfg.get("radius", 8)))))
            col = cfg.get("color", [255, 215, 0, 150])
            if len(col) >= 4:
                r, g, b, a = [int(x) for x in col[:4]]
            else:
                r, g, b = [int(x) for x in col[:3]]
                a = 150
            freq = float(cfg.get("freq", 0.8))
            self.aura = {
                "radius": rad,
                "rgb": (r, g, b),
                "alpha": int(max(0, min(255, a))),
                "freq": freq,
                "t": 0.0,
                "layers": {d: [None] * len(self.frames[d]) for d in self.frames},
            }
        except Exception:
            self.aura = None

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

    def _ensure_aura_layers(self, d, fidx):
        """Baut für (Richtung d, Frame fidx) die skalierten Ring-Silhouetten.
           Verwendet die vorhandene Walk-Maske -> echte Silhouette."""
        if not self.aura: return None
        layers = self.aura["layers"][d]
        if layers[fidx] is not None:
            return layers[fidx]

        rad = self.aura["radius"]; (cr,cg,cb) = self.aura["rgb"]
        frm = self.frames[d][fidx]; msk = self.masks[d][fidx]
        w, h = frm.get_width(), frm.get_height()

        # Basis-Silhouette in Farbe (Alpha 255), wird pro Ring skaliert
        base = msk.to_surface(setcolor=(cr,cg,cb,255), unsetcolor=(0,0,0,0)).convert_alpha()

        ring_surfs = [None]*(rad+1)  # Index = i (1..rad)
        for i in range(1, rad+1):
            # ring ist um i Pixel größer in beide Richtungen
            ring = pygame.transform.smoothscale(base, (w + 2*i, h + 2*i))
            ring_surfs[i] = ring

        layers[fidx] = ring_surfs
        return ring_surfs

    def update(self, dt):
        # Aura-Zeit fortschreiben (und ggf. „reparieren“, falls jemand self.aura ersetzt hat)
        if self.aura and ("t" not in self.aura or "layers" not in self.aura):
            # self.aura enthält dann vermutlich nur die Roh-Config -> neu initialisieren
            self._init_aura(self.aura)
        if self.aura:
            self.aura["t"] += dt
        if self.dead or self.seg >= len(self.path)-1: return
        if self.aura: self.aura["t"] += dt
        if self.hit_active and self.hit_frames:
            self.hit_anim_accum += dt
            step_hit = 1.0 / max(1e-6, self.etype.hit_fps)
            while self.hit_anim_accum >= step_hit:
                self.hit_anim_accum -= step_hit
                self.hit_index += 1
                if self.hit_index >= len(self.hit_frames[self.dir]):
                    self.hit_active=False; self.hit_index=0; break
            return
        v = self.speed
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

    def is_offscreen(self, margin=40):
        frm = (self.hit_frames[self.dir][self.hit_index] if (self.hit_active and self.hit_frames)
               else self.frames[self.dir][self.findex])
        ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax); tly = int(self.fy - ay)
        w, h = frm.get_width(), frm.get_height()
        return (tlx + w < -margin or tlx > WIDTH + margin or
                tly + h < -margin or tly > HEIGHT + margin)

    def feet_offscreen(self, margin=6):
        return (self.fx < -margin or self.fx > WIDTH + margin or
                self.fy < -margin or self.fy > HEIGHT + margin)

    def draw(self, screen):
        if self.dead: return
        if self.hit_active and self.hit_frames:
            frm = self.hit_frames[self.dir][self.hit_index]
            ax, ay = (self.hit_anchor[self.dir] if self.hit_anchor else self.walk_anchor[self.dir])
        else:
            frm = self.frames[self.dir][self.findex]
            ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax); tly = int(self.fy - ay)
        if (tlx + frm.get_width() < 0 or tlx > WIDTH or
            tly + frm.get_height() < 0 or tly > HEIGHT):
            return
        # ---- Aura zeichnen (hinter dem Sprite)
        if self.aura:
            rings = self._ensure_aura_layers(self.dir, self.findex)
            if rings:
                # Pulsfaktor 0.7..1.0
                t = self.aura["t"]; f = self.aura["freq"]
                pulse = 0.7 + 0.25 * (0.5 * (1.0 + math.sin(2.0*math.pi*f*t)))
                base_a = self.aura["alpha"]
                rad = self.aura["radius"]

                # Von außen nach innen, innerer Bereich deckender
                for i in range(rad, 0, -1):
                    ring = rings[i]
                    if not ring: continue
                    # Quadratische Falloff-Kurve: innen heller, außen transparenter
                    inner = 1.0 - ((i-1)/rad)
                    a = int(max(0, min(255, base_a * (inner*inner) * pulse)))
                    ring.set_alpha(a)
                    # Offset: größere Ringe beginnen weiter oben/links
                    off = rad - i
                    screen.blit(ring, (tlx - off, tly - off))

        screen.blit(frm,(tlx,tly))

    def _local_hit_pos(self, mx,my):
        frm = self.frames[self.dir][self.findex]  # Maske aus Walk (solide)
        ax, ay = self.walk_anchor[self.dir]
        tlx = int(self.fx - ax); tly = int(self.fy - ay)
        rx,ry = mx - tlx, my - tly
        if 0 <= rx < frm.get_width() and 0 <= ry < frm.get_height():
            return (rx,ry)
        return None

    def hit_kind(self, mx,my, head_frac=None):
        pos = self._local_hit_pos(mx,my)
        if pos is None: return "none"
        rx,ry = pos
        m = self.masks[self.dir][self.findex]
        if not m.get_at((int(rx),int(ry))): return "none"
        brs = m.get_bounding_rects()
        br = brs[0] if brs else pygame.Rect(0,0,*m.get_size())
        frac = head_frac if head_frac is not None else getattr(self.etype, "headshot_top", 0.22)
        frac = max(0.05, min(0.9, float(frac)))
        head_h = max(1, int(br.h * frac))
        head_rect = pygame.Rect(br.x, br.y, br.w, head_h)
        return "head" if head_rect.collidepoint(rx,ry) else "body"

# ===== Intro / World Select ====================================================
def load_world_intro(world):
    """Liest optional <World>_intro.json mit {highlight:{x,y,r}, text:"..." }"""
    base = os.path.join(ASSET_ROOT, "pics/TowerDefence/Worlds", world)
    p = os.path.join(base, f"{world}_intro.json")
    data = {}
    if os.path.isfile(p):
        try: data = load_json_relaxed(p)
        except Exception as e: print(f"[WARN] {world}_intro.json fehlerhaft:", e)
    return data

def draw_world_select(screen, worlds, sel_idx, font_title, font_item):
    screen.fill((25,40,38))
    title = font_title.render("Wähle eine Welt", True, (230,255,230))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 24))

    # Layout: links 1/3 Textliste, rechts 2/3 Bild
    margin  = 24
    left_w  = WIDTH // 3
    right_w = WIDTH - left_w - margin*2
    right_h = HEIGHT - 180

    # Liste links (1/3)
    left_x = margin
    top_y  = 110
    for i, w in enumerate(worlds):
        col = (255,255,255) if i==sel_idx else (200,200,200)
        it  = font_item.render(w, True, col)
        screen.blit(it, (left_x, top_y + i*(it.get_height()+10)))

    # Preview rechts (2/3)
    if worlds:
        wname = worlds[sel_idx]
        img = world_full_image(wname)
        if img:
            iw, ih = img.get_size()
            # proportional auf 2/3-Bereich skalieren
            scale = min(right_w / iw, right_h / ih)
            img = pygame.transform.smoothscale(img, (int(iw*scale), int(ih*scale)))
            # rechtsbündig in den 2/3-Bereich einsetzen
            x = WIDTH - margin - img.get_width()
            y = 100
            screen.blit(img, (x, y))

    hint = font_item.render("ENTER = Start  •  Pfeile = Auswahl", True, (235,235,235))
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-50))

def draw_world_intro(screen, wname, img_full, intro_cfg, t):
    """Kurzer Einspieler: Zeige Karte, pulsiere Highlight und Text."""
    screen.fill((0,0,0))
    if img_full:
        img = pygame.transform.smoothscale(img_full, (WIDTH, HEIGHT))
        screen.blit(img, (0,0))
    # Highlight
    hi = (intro_cfg.get("highlight") if isinstance(intro_cfg.get("highlight"), dict) else {})
    hx = hi.get("x", WIDTH//2); hy = hi.get("y", HEIGHT//2); hr = hi.get("r", 120)
    # Puls
    k = (math.sin(t*2.6)+1.0)/2.0
    r  = int(hr * (0.85 + 0.25*k))
    a  = int(120 + 80*k)
    glow = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (60,255,120,a), (r+1, r+1), r, 8)
    screen.blit(glow, (hx - r, hy - r))

    # Text
    text = intro_cfg.get("text") or "Beschützen Sie die Statue in der Mitte."
    font_big = pygame.font.SysFont(None, 58, bold=True)
    font_small = pygame.font.SysFont(None, 28, bold=False)

    msg = font_big.render(text, True, (255,255,210))
    sh  = font_big.render(text, True, (0,0,0))
    cx = WIDTH//2
    screen.blit(sh,  (cx - sh.get_width()//2 + 2, 40 + 2))
    screen.blit(msg, (cx - msg.get_width()//2, 40))

    hint = font_small.render("Drücke ENTER, um Level 1 zu starten", True, (255,255,255))
    sh2  = font_small.render("Drücke ENTER, um Level 1 zu starten", True, (0,0,0))
    screen.blit(sh2, (cx - sh2.get_width()//2 + 2, HEIGHT - 70 + 2))
    screen.blit(hint,(cx - hint.get_width()//2, HEIGHT - 70))

# ===== LevelState ==============================================================
class LevelState:
    def __init__(self, bg, paths_dict, enemy_types, gameplay_cfg, waves, overlays, mods):
        # --- Assets / Scene ---
        self.bg = bg
        self.paths = paths_dict                # {"0":[(x,y),...], ...}
        self.enemy_types = enemy_types         # {"Zombie": EnemyType(...), ...}
        self.overlays = overlays or []         # [{surf, active, blocks, trigger, ...}, ...]
        self.enemies = []
        self.effects = []
        self.floaters = []
        self.power_fx = []
        self.paused = False

        # --- Waves / Progress ---
        self.waves = list(waves or [])
        self.wave_index = 0
        self.wave_time = 0.0
        self.spawn_queue = []
        self.current_wave_mods = {}

        # --- Start-/Intro-Steuerung ---
        self.waiting_start = True              # wenn True → Start-Overlay (oder Boss-Intro)
        self.boss_intro_active = False         # Intro-Bildschirm mit Boss rechts/links etc.

        # --- Boss / Boss-Text ---
        self.boss = None                       # wird über attach_boss_from_level_cfg gesetzt
        self.attack_msg = "Angriff!!!"
        self.attack_msg_t = 0.0                # >0.0 → im Render die „Angriff!!!“-Anzeige
        self.end_msg = "Auf zum nächsten Angriffspunkt!"
        self.end_shout_t = 0.0                 # >0.0 → End-Text anzeigen
        self.end_text_duration = 1.6           # Dauer des End-Textes (Sek.)
        self._boss_attack_duration = 0.9       # wie lange die Attack-Animation laufen soll

        # --- Gameplay Werte/Upgrades ---
        self.gameplay_cfg = gameplay_cfg or {}
        self.mods = mods if isinstance(mods, dict) else {}

        self.firepower = int(self.gameplay_cfg.get("base_firepower", 1))
        self.upgrade_threshold = int(self.gameplay_cfg.get("upgrade_threshold", 50))
        self.upgrade_amount = int(self.gameplay_cfg.get("upgrade_amount", 1))
        self.max_firepower = int(self.gameplay_cfg.get("max_firepower", 10))
        self.score = 0
        self.next_upgrade_at = self.upgrade_threshold
        self.kills = 0

        # --- Leben/Entkommen ---
        self.escapes = 0
        self.max_escapes = 3
        self.game_over = False

        # --- Fonts/HUD ---
        self.font_hud     = pygame.font.SysFont(None, 30, bold=False)
        self.font_floater = pygame.font.SysFont(None, 48, bold=True)
        self.font_debug   = pygame.font.SysFont(None, 24, bold=False)
        self.font_big     = pygame.font.SysFont(None, 56, bold=True)
        self.font_end     = pygame.font.SysFont(None, 72, bold=True)

        # Debug/UX
        self.last_click = None

    # ===================== Boss / Intro ===================================

    def attach_boss_from_level_cfg(self):
        cfg = self.mods.get("__boss_cfg__") or {}
        if not isinstance(cfg, dict) or not cfg:
            return

        enemy = str(cfg.get("enemy") or "TheSmith")
        pos = cfg.get("pos") or cfg.get("feet") or [760, 620]
        scale = float(cfg.get("scale", 1.0))
        text = cfg.get("text") or cfg.get("shout") or "Angriff!!!"

        # Text-Dauer (Sekunden) – auch "1500ms" möglich
        tdur = cfg.get("text_duration", 1.2)
        try:
            self._attack_text_duration = (
                float(tdur) if isinstance(tdur, (int, float))
                else (float(str(tdur).replace("ms", "")) / 1000.0 if "ms" in str(tdur) else float(tdur))
            )
        except Exception:
            self._attack_text_duration = 1.2

        # End-Spruch (+ Dauer) optional
        end_text = str(cfg.get("end_text", "") or "").strip()
        if end_text:
            self._end_msg = self.font_end.render(end_text, True, (255, 255, 255))
            self._end_msg_shadow = self.font_end.render(end_text, True, (0, 0, 0))
        else:
            self._end_msg = self._end_msg_shadow = None
        try:
            self._end_text_duration = float(cfg.get("end_text_duration", getattr(self, "_end_text_duration", 1.2)))
        except Exception:
            self._end_text_duration = 1.2

        # Attack-Süd-Atlas laden
        folder = os.path.join(ASSET_ROOT, "pics/TowerDefence", "Enemies", enemy)
        jj = os.path.join(folder, f"{enemy.lower()}_attack.json")
        if not os.path.isfile(jj):
            jj = os.path.join(folder, "thesmith_attack.json")
        atlas = load_grid_atlas(jj, folder, fallbacks=("attack.png",))
        frames_s = atlas["frames"].get("S") or atlas["frames"].get("s")
        anchor_s = atlas["anchors"].get("S") or atlas["anchors"].get("s")
        if not frames_s:
            print("[BOSS] Kein S-Angriff in", enemy);
            return

        # BossProp erzeugen und JSON-Pos/Scale anwenden
        self.boss = BossProp(frames_s, anchor_s, (int(pos[0]), int(pos[1])), fps=10, scale=scale)
        self._attack_msg = self.font_end.render(str(text), True, (255, 255, 255))
        self._attack_msg_shadow = self.font_end.render(str(text), True, (0, 0, 0))

    def prepare_boss_intro_from_level(self):
        """
        Aktiviert das Boss-Intro-Overlay:
        - Bild links aus Enemies/<enemy>/intro.png
        - Text rechts aus level_json["boss_intro"]["text"]
        """
        if not self.boss:
            return

        cfg_intro = (self.mods.get("__boss_intro__") or {})
        if not bool(cfg_intro.get("show", True)):
            # kein Intro gewünscht
            self.boss_intro_active = False
            return

        # Bild aus dem Enemies-Ordner des Bosses laden
        enemy = (self.mods.get("__boss_cfg__") or {}).get("enemy") or "TheSmith"
        folder = os.path.join(ASSET_ROOT, "pics/TowerDefence", "Enemies", enemy)
        p_intro = os.path.join(folder, "intro.png")
        img = try_load(p_intro)

        # sanft auf max. ~70% Höhe skalieren (optional, falls groß)
        if img:
            max_h = int(HEIGHT * 0.70)
            if img.get_height() > max_h:
                scale = max_h / float(img.get_height())
                img = pygame.transform.smoothscale(
                    img, (int(img.get_width() * scale), max_h)
                )

        self.boss_intro_img = img  # linke Seite
        self.boss_intro_text = str(cfg_intro.get("text") or "")  # rechte Seite
        self.boss_intro_alpha = int(cfg_intro.get("bg_alpha", 200))

        self.boss_intro_active = True
        self.waiting_start = True  # Intro offen ⇒ wir warten auf ENTER/Auto-Start

    def trigger_attack_shout(self):
        if self.boss:
            self.boss.play_for(max(0.7, len(self.boss.frames) / max(1.0, self.boss.fps)))
        self.attack_msg_t = max(self.attack_msg_t, float(getattr(self, "_attack_text_duration", 1.2)))

    def trigger_end_shout(self):
        """Am Ende eines Levels (oder wenn du es explizit willst)."""
        self.end_shout_t = float(self.end_text_duration)

    # ===================== UI/HUD/Utils ====================================

    def _maybe_upgrade(self):
        changed = False
        while self.score >= self.next_upgrade_at and self.firepower < self.max_firepower:
            self.firepower += self.upgrade_amount
            self.next_upgrade_at += self.upgrade_threshold
            changed = True
        if changed:
            self.power_fx.append(PowerUpEffect(f"Firepower +{self.upgrade_amount}!"))

    def spawn_floater(self, text, world_fx, world_fy, frame, anchor):
        ax, ay = anchor
        tlx = int(world_fx - ax); tly = int(world_fy - ay)
        x = tlx + frame.get_width() // 2; y = tly - 10
        self.floaters.append(FloatingText(text, x, y, self.font_floater))

    def overlay_blocks_at(self, x, y):
        """True, wenn aktives Overlay an (x,y) opak ist."""
        xi, yi = int(x), int(y)
        if not (0 <= xi < WIDTH and 0 <= yi < HEIGHT):
            return False
        for ov in self.overlays:
            if not ov["active"] or not ov.get("blocks", True):
                continue
            a = ov["surf"].get_at((xi, yi)).a
            if a > OVERLAY_BLOCK_ALPHA:
                return True
        return False

    def draw_hud(self, screen):
        blit_text_outline(screen, self.font_hud, f"Firepower: {self.firepower}",
                          (WIDTH-10, 8), color=(255,255,255), outline=(0,0,0), w=2, align_right=True)
        if self.firepower < self.max_firepower:
            tneeded = self.next_upgrade_at
            remaining = max(0, tneeded - self.score)
            s = f"Score: {self.score}/{tneeded}  (noch {remaining})"
        else:
            s = f"Score: {self.score}  (Max Firepower)"
        blit_text_outline(screen, self.font_hud, s,
                          (WIDTH-10, 8 + 34), color=(255,255,255), outline=(0,0,0), w=2, align_right=True)
        lifes = self.font_hud.render(f"Durchgelassen: {self.escapes}/{self.max_escapes}", True, (255,40,40))
        screen.blit(lifes, (WIDTH - lifes.get_width() - 10, 8 + 34 + 32))
        if self.last_click:
            cx, cy = self.last_click
            blit_text_outline(screen, self.font_debug, f"Click: {int(cx)}, {int(cy)}",
                              (WIDTH-10, 8 + 34 + 32 + lifes.get_height() + 8),
                              color=(255,255,255), outline=(0,0,0), w=2, align_right=True)

    # ===================== Treffer / Schuss ================================

    def apply_hit(self, mx, my):
        if self.game_over or self.waiting_start or self.boss_intro_active:
            return False
        if self.overlay_blocks_at(mx, my):
            return False

        # von oben nach unten → zuletzt gezeichneter Gegner zuerst
        for e in reversed(self.enemies):
            if e.dead:
                continue
            kind = e.hit_kind(mx,my)
            if kind == "none":
                continue

            damage = max(1, self.firepower)
            if kind == "head":
                if e.headshot_instant_kill:
                    e.hp = 0
                else:
                    damage = max(1, int(round(damage * e.headshot_mul)))

            if not (kind == "head" and e.headshot_instant_kill):
                e.hp -= damage

            if e.hp <= 0:
                frm = e.frames[e.dir][e.findex]
                self.spawn_floater(f"+{e.score}", e.fx, e.fy, frm, e.walk_anchor[e.dir])
                self.effects.append(ExplosionEffect(
                    e.death[e.dir], (int(e.fx),int(e.fy)),
                    frm, e.death_anchor[e.dir],
                    death_fps=e.etype.death_fps))
                e.dead = True
                self.kills += 1
                self.score += e.score
                self._maybe_upgrade()
            else:
                if e.hit_frames:
                    e.hit_active = True
                    e.hit_index = 0
                    e.hit_anim_accum = 0.0
                self.effects.append(HitPopEffect((e.fx, e.fy)))
            return True
        return False

    # ===================== Waves / Spawning ================================

    def _start_wave(self, ix):
        """interner Start einer Welle ix"""
        if ix >= len(self.waves):
            return False
        wv = self.waves[ix]
        self.spawn_queue = list(wv.get("spawns", []))
        self.spawn_queue.sort(key=lambda s: s.get("t", 0.0))
        self.current_wave_mods = wv.get("mods", {}) or {}
        self.wave_time = 0.0
        return True

    def on_press_enter(self):
        """Von außen aufgerufen, wenn Enter gedrückt wurde (Start/weiter)."""
        if self.boss_intro_active:
            # Intro schließen → direkt starten
            self.boss_intro_active = False
            self.waiting_start = False
            # sofortige Attack-Animation + Text
            self.trigger_attack_shout()
            self._start_wave(self.wave_index)
            return

        if self.waiting_start:
            self.waiting_start = False
            # Falls noch keine Welle läuft → starten
            if not self.spawn_queue and self.wave_index < len(self.waves):
                self.trigger_attack_shout()
                self._start_wave(self.wave_index)

    def update_spawning(self, dt):
        if self.game_over:
            return

        # Welche Gegner „leben“ (nicht tot/entkommen)?
        def alive_enemies():
            alive = []
            for e in self.enemies:
                if e.dead:
                    continue
                at_end = (e.seg >= len(e.path) - 1)
                if at_end and (e.is_offscreen(margin=12) or e.feet_offscreen(margin=2)):
                    continue
                alive.append(e)
            return alive

        # Neue Welle starten?
        if self.wave_index < len(self.waves):
            # Welle noch nicht geladen?
            if not self.spawn_queue and self.wave_time == 0.0:
                if self.wave_index == 0:
                    # Erste Welle: warten, bis waiting_start False ist
                    if not self.waiting_start and not self.boss_intro_active:
                        self.trigger_attack_shout()
                        self._start_wave(self.wave_index)
                else:
                    if not alive_enemies():
                        # Folge-Wellen: abhängig von require_enter
                        nxt = self.waves[self.wave_index]
                        if bool(nxt.get("require_enter", False)):
                            if not self.waiting_start and not self.boss_intro_active:
                                self.trigger_attack_shout()
                                self._start_wave(self.wave_index)
                        else:
                            self.trigger_attack_shout()
                            self._start_wave(self.wave_index)

        # Wenn wir noch am Start-Overlay/Intro stehen → keine Zeit zählen
        if self.waiting_start or self.boss_intro_active:
            return

        # Laufende Welle: spawnen, sobald Zeit erreicht
        if self.spawn_queue:
            self.wave_time += dt
            while self.spawn_queue and self.spawn_queue[0].get("t", 0.0) <= self.wave_time:
                s = self.spawn_queue.pop(0)
                typ = s.get("type", "Zombie")
                path_key = str(s.get("path", "0")).lower()
                path_pts = self.paths.get(path_key) or next(iter(self.paths.values()))

                # Mods-Vererbung (Level/Wave/Spawn)
                lvl_all = self.mods.get("all", {});      lvl_typ = self.mods.get(typ, {})
                wav_all = self.current_wave_mods.get("all", {}); wav_typ = self.current_wave_mods.get(typ, {})

                def pget(field, default=None):
                    v = s.get(field, None)
                    if v is None: v = wav_typ.get(field, None)
                    if v is None: v = wav_all.get(field, None)
                    if v is None: v = lvl_typ.get(field, None)
                    if v is None: v = lvl_all.get(field, None)
                    return default if v is None else v

                hp_base = int(pget("hp", self.gameplay_cfg.get("default_hp", 3)))
                hp_mul_total = 1.0
                for v in (lvl_all.get("hp_mul"), lvl_typ.get("hp_mul"), wav_all.get("hp_mul"),
                          wav_typ.get("hp_mul"), s.get("hp_mul")):
                    if v is not None:
                        try: hp_mul_total *= float(v)
                        except: pass
                hp = int(max(0, round(hp_base * hp_mul_total)))

                score_base = int(pget("score", self.gameplay_cfg.get("default_score", 10)))
                score_mul_total = 1.0
                for v in (lvl_all.get("score_mul"), lvl_typ.get("score_mul"), wav_all.get("score_mul"),
                          wav_typ.get("score_mul"), s.get("score_mul")):
                    if v is not None:
                        try: score_mul_total *= float(v)
                        except: pass
                score = int(max(0, round(score_base * score_mul_total)))

                scale = float(pget("scale", self.gameplay_cfg.get("default_scale", 1.0)))
                speed = float(pget("move_speed", self.gameplay_cfg.get("default_speed", 95.0)))
                hmul  = float(pget("headshot_mul", self.gameplay_cfg.get("default_headshot_mul", 2.0)))
                hkill = bool(pget("headshot_instant_kill", False))
                aura_cfg = s.get("aura") if isinstance(s.get("aura"), dict) else None

                enemy = Enemy(self.enemy_types[typ], path_pts,
                              hp=hp, score=score,
                              headshot_mul=hmul, headshot_instant_kill=hkill,
                              speed=speed, scale=scale, aura=aura_cfg)
                enemy.spawn_id = s.get("id")
                self.enemies.append(enemy)

        # Welle abgeschlossen? → nächste vorbereiten/ENTER ggf. nötig
        if not self.spawn_queue and not alive_enemies() and self.wave_index < len(self.waves):
            self.wave_index += 1
            self.wave_time = 0.0
            if self.wave_index < len(self.waves) and bool(self.waves[self.wave_index].get("require_enter", False)):
                self.waiting_start = True
            else:
                # Auto-Start der nächsten Welle
                self.trigger_attack_shout()
                self._start_wave(self.wave_index)

    # ===================== Overlays / Trigger ==============================

    def update_overlay_triggers(self):
        """Aktiviere Overlays, deren Trigger erreicht wurde (mit Filtern)."""
        for ov in self.overlays:
            tr = ov.get("trigger")
            if not tr or ov["active"]:
                continue
            tx, ty, r = tr["x"], tr["y"], tr["r"]
            r2 = r*r
            for e in self.enemies:
                if e.dead:
                    continue
                if ov.get("only_type") and e.etype.name != ov["only_type"]:
                    continue
                if ov.get("only_spawn_id") and e.spawn_id != ov["only_spawn_id"]:
                    continue
                dx = e.fx - tx; dy = e.fy - ty
                if dx*dx + dy*dy <= r2:
                    ov["active"] = True
                    break

# ===== MAIN ===================================================================
def main():
    pygame.init()
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1)
    except TypeError:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("TowerDefence — Worlds")
    clock = pygame.time.Clock()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    # Gegner laden
    ENEMY_TYPES = {}
    enemies_root = os.path.join(ASSET_ROOT, "pics/TowerDefence/Enemies")
    global_cfg = read_global_enemy_cfg()
    if os.path.isdir(enemies_root):
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

    # ---- WORLDS
    worlds = discover_worlds()
    if not worlds:
        raise SystemExit("Keine Welten in pics/TowerDefence/Worlds/ gefunden.")
    world_idx = 0
    world_mode = "select"  # "select" -> "intro" -> "game"

    # Platzhalter für laufendes Level
    world_name = worlds[world_idx]
    levels = discover_levels(world_name)
    if not levels:
        raise SystemExit(f"Keine Level in World '{world_name}' gefunden.")
    level_index = 0
    sublevels = discover_sublevels(world_name, levels[level_index])
    sub_index = 0

    def build_state(world, level_folder, subname, img_path):
        bg = try_load(img_path)
        if bg is None:
            bg = pygame.Surface((WIDTH, HEIGHT))
            bg.fill((40, 60, 40))
        else:
            bg = pygame.transform.smoothscale(bg, (WIDTH, HEIGHT))
        paths_dict, waves, overlay_rules, mods = load_level_spec(world, level_folder, subname, ENEMY_TYPES)
        overlays = load_overlays(world, level_folder, subname, overlay_rules)
        return LevelState(bg, paths_dict, ENEMY_TYPES, gameplay_cfg, waves, overlays, mods)

    # Intro-Setup (Welt-Intro, nicht Boss-Intro)
    intro_img = None
    intro_cfg = {}

    # Fadenkreuz (klein)
    cross = pygame.Surface((22, 22), pygame.SRCALPHA)
    pygame.draw.circle(cross, (255, 255, 255), (11, 11), 10, 1)
    pygame.draw.line(cross, (255, 255, 255), (0, 11), (22, 11), 1)
    pygame.draw.line(cross, (255, 255, 255), (11, 0), (11, 22), 1)
    cross_pos = None
    cross_until = 0

    # Fonts für World-UI
    font_title = pygame.font.SysFont(None, 64, bold=True)
    font_item  = pygame.font.SysFont(None, 36, bold=False)

    # Game-State placeholder
    state = None
    level_overlay = None
    pending_next = None  # (world_name, levels, level_index, sublevels, sub_index, next_label)

    t_intro = 0.0

    running = True
    while running and hm_game_active():
        dt = clock.tick(FPS) / 1000.0

        # ---------------------- Events ----------------------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.KEYDOWN:
                # Global
                if ev.key == pygame.K_ESCAPE:
                    running = False

                # ---------------- Welt-Auswahl ----------------
                if world_mode == "select":
                    if ev.key == pygame.K_UP:
                        world_idx = (world_idx - 1) % len(worlds)
                    elif ev.key == pygame.K_DOWN:
                        world_idx = (world_idx + 1) % len(worlds)
                    elif ev.key == pygame.K_RETURN:
                        # Auswahl -> Intro vorbereiten
                        world_name = worlds[world_idx]
                        levels = discover_levels(world_name)
                        if not levels:
                            continue
                        level_index = 0
                        sublevels = discover_sublevels(world_name, levels[level_index])
                        sub_index = 0
                        intro_img = world_full_image(world_name)
                        intro_cfg = load_world_intro(world_name)
                        world_mode = "intro"
                        t_intro = 0.0

                # ---------------- Welt-Intro ------------------
                elif world_mode == "intro":
                    if ev.key == pygame.K_RETURN:
                        # Level-State anlegen
                        subname, img_path = sublevels[sub_index]
                        state = build_state(world_name, levels[level_index], subname, img_path)
                        # Boss & Intro (aus Level-JSON)
                        state.attach_boss_from_level_cfg()
                        state.prepare_boss_intro_from_level()
                        # In den Spielmodus wechseln; wir warten zunächst auf Start (Intro offen)
                        world_mode = "game"
                        level_overlay = None
                        pending_next = None
                        state.waiting_start = True
                        continue

                # ---------------- Game ------------------------
                elif world_mode == "game":
                    # ENTER: Start/Welle/Levelende weiter
                    if ev.key == pygame.K_RETURN:
                        if state is None:
                            # Safety
                            subname, img_path = sublevels[sub_index]
                            state = build_state(world_name, levels[level_index], subname, img_path)
                            state.attach_boss_from_level_cfg()
                            state.prepare_boss_intro_from_level()
                            state.waiting_start = True
                            continue

                        # Boss-Intro schließen -> sofort Welle starten
                        if getattr(state, "boss_intro_active", False):
                            state.boss_intro_active = False
                            # Falls wir noch im Start-Warten sind, sofort starten:
                            if getattr(state, "waiting_start", False):
                                state.on_press_enter()
                            continue

                        # Start der ersten/nächsten Welle (falls noch Start-Overlay)
                        if getattr(state, "waiting_start", False):
                            state.on_press_enter()
                            continue

                        # Level-Ende-Overlay -> weiter
                        if level_overlay is not None:
                            if pending_next:
                                # Kampagnenwerte sichern
                                prev_fire = getattr(state, 'firepower', 1)
                                prev_score = getattr(state, 'score', 0)
                                prev_next = getattr(state, 'next_upgrade_at', 50)
                                # nächstes Level/Sublevel laden
                                world_name, levels, level_index, sublevels, sub_index, _ = pending_next
                                subname, img_path = sublevels[sub_index]
                                state = build_state(world_name, levels[level_index], subname, img_path)
                                state.attach_boss_from_level_cfg()
                                state.prepare_boss_intro_from_level()
                                # Werte wiederherstellen
                                state.firepower = prev_fire
                                state.score = prev_score
                                state.next_upgrade_at = prev_next
                                level_overlay = None
                                pending_next = None
                            continue

                    # SPACE: Pause
                    elif ev.key == pygame.K_SPACE and state and not state.game_over:
                        state.paused = not state.paused

                    # Debug: N = nächster Sublevel/Level
                    elif ev.key == pygame.K_n and state:
                        prev_fire = getattr(state, 'firepower', 1)
                        prev_score = getattr(state, 'score', 0)
                        prev_next = getattr(state, 'next_upgrade_at', 50)

                        nxt = None
                        nxt_si = sub_index + 1
                        if nxt_si >= len(sublevels):
                            nxt_li = level_index + 1
                            if nxt_li < len(levels):
                                nsubs = discover_sublevels(world_name, levels[nxt_li])
                                if nsubs:
                                    nxt = (world_name, levels, nxt_li, nsubs, 0,
                                           get_level_title(world_name, levels[nxt_li], nsubs[0][0]))
                        else:
                            nxt = (world_name, levels, level_index, sublevels, nxt_si,
                                   get_level_title(world_name, levels[level_index], sublevels[nxt_si][0]))

                        if nxt:
                            world_name, levels, level_index, sublevels, sub_index, _ = nxt
                            subname, img_path = sublevels[sub_index]
                            state = build_state(world_name, levels[level_index], subname, img_path)
                            state.attach_boss_from_level_cfg()
                            state.prepare_boss_intro_from_level()
                            state.firepower = prev_fire
                            state.score = prev_score
                            state.next_upgrade_at = prev_next
                            level_overlay = None
                            pending_next = None
                        else:
                            world_mode = "select"
                            continue

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if world_mode == "game" and state and not state.game_over and level_overlay is None:
                    mx, my = ev.pos
                    state.last_click = (mx, my)
                    cross_pos = (mx - cross.get_width() // 2, my - cross.get_height() // 2)
                    cross_until = pygame.time.get_ticks() + 120
                    state.apply_hit(mx, my)

        # HM-Systeme Schuss
        if world_mode == "game" and state and not state.game_over and level_overlay is None and not getattr(state, "boss_intro_active", False) and not getattr(state, "waiting_start", False) and hm_hit_detected():
            pos = hm_get_pos()
            if pos:
                mx, my = pos
                state.last_click = (mx, my)
                cross_pos = (mx - cross.get_width() // 2, my - cross.get_height() // 2)
                cross_until = pygame.time.get_ticks() + 120
                state.apply_hit(mx, my)

        # ---------------------- Updates ---------------------
        if world_mode == "game" and state:
            # Auto-Start, falls Intro bereits geschlossen ist, wir aber noch warten
            if getattr(state, "waiting_start", False) and not getattr(state, "boss_intro_active", False):
                state.on_press_enter()

            if state and not state.game_over and level_overlay is None and not getattr(state, "paused", False):
                state.update_spawning(dt)
                for e in state.enemies:
                    e.update(dt)
                state.update_overlay_triggers()

                # Gegnerliste ausdünnen (entkommen/weg)
                pruned = []
                for e in state.enemies:
                    if e.dead:
                        continue
                    at_end = (e.seg >= len(e.path) - 1)
                    if at_end and (e.is_offscreen(margin=12) or e.feet_offscreen(margin=2)):
                        state.escapes += 1
                        continue
                    pruned.append(e)
                state.enemies = pruned

                # Effekte / Floater / PowerUps
                for eff in list(state.effects):
                    eff.update(dt)
                    if eff.finished():
                        state.effects.remove(eff)
                for ft in list(state.floaters):
                    ft.update(dt)
                    if ft.finished():
                        state.floaters.remove(ft)
                for pfx in list(state.power_fx):
                    pfx.update(dt)
                    if pfx.finished():
                        state.power_fx.remove(pfx)

            # Boss-Animation updaten + Text-Timer runterzählen
            if getattr(state, "boss", None):
                state.boss.update(dt)

            if getattr(state, "attack_msg_t", 0.0) > 0.0:
                state.attack_msg_t = max(0.0, state.attack_msg_t - dt)

            if getattr(state, "end_shout_t", 0.0) > 0.0:
                state.end_shout_t = max(0.0, state.end_shout_t - dt)

            # Game Over?
            if not state.game_over and state.escapes > state.max_escapes:
                state.game_over = True

            # Levelende? (keine Spawns, keine Alive-Gegner, keine Effekte, alle Wellen durch)
            if (not state.game_over
                    and level_overlay is None
                    and not state.waiting_start):
                alive_left = [e for e in state.enemies if not e.dead]
                all_waves_done = (not hasattr(state, "waves")) or (state.wave_index >= len(state.waves))
                if not state.spawn_queue and not alive_left and not state.effects and all_waves_done:
                    # Nächstes Sublevel/Level bestimmen
                    nxt = None
                    nxt_si = sub_index + 1
                    if nxt_si >= len(sublevels):
                        nxt_li = level_index + 1
                        if nxt_li < len(levels):
                            nsubs = discover_sublevels(world_name, levels[nxt_li])
                            if nsubs:
                                nxt = (world_name, levels, nxt_li, nsubs, 0,
                                       get_level_title(world_name, levels[nxt_li], nsubs[0][0]))
                    else:
                        nxt = (world_name, levels, level_index, sublevels, nxt_si,
                               get_level_title(world_name, levels[level_index], sublevels[nxt_si][0]))

                    stats = {"firepower": state.firepower, "score": state.score,
                             "kills": state.kills, "escapes": state.escapes, "max_escapes": state.max_escapes}
                    if nxt is not None:
                        pending_next = nxt
                        level_overlay = LevelEndOverlay(stats, nxt[5])
                    else:
                        # Welt abgeschlossen -> zurück zur Weltwahl
                        world_mode = "select"
                        continue

        # ---------------------- Render ----------------------
        if world_mode == "select":
            draw_world_select(screen, worlds, world_idx, font_title, font_item)

        elif world_mode == "intro":
            t_intro += dt
            draw_world_intro(screen, world_name, intro_img, intro_cfg, t_intro)

        elif world_mode == "game":
            if state:
                # Hintergrund
                screen.blit(state.bg, (0, 0))

                # Gegner/Effekte
                for e in state.enemies:
                    e.draw(screen)
                for eff in state.effects:
                    eff.draw(screen)

                # Boss
                if getattr(state, "boss", None):
                    state.boss.draw(screen)

                # Overlays (jetzt ganz oben)
                for ov in state.overlays:
                    if ov["active"]:
                        screen.blit(ov["surf"], (0, 0))

                # Floater/PowerFX/HUD
                for ft in state.floaters:
                    ft.draw(screen)
                for pfx in state.power_fx:
                    pfx.draw(screen, state.font_big)
                state.draw_hud(screen)

                # ---- Boss-Intro-Overlay (Bild links, Text rechts) ----
                if getattr(state, "boss_intro_active", False):
                    # Abdunkeln
                    alpha = int(getattr(state, "boss_intro_alpha", 200))
                    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    ov.fill((0, 0, 0, max(0, min(255, alpha))))
                    screen.blit(ov, (0, 0))
                    # Bild links
                    if getattr(state, "boss_intro_img", None):
                        img = state.boss_intro_img
                        x = int(WIDTH * 0.08)
                        y = HEIGHT // 2 - img.get_height() // 2
                        screen.blit(img, (x, y))
                    # Text rechts (Wrap)
                    tx = int(WIDTH * 0.55)
                    maxw = WIDTH - tx - 40
                    lines = wrap_lines(state.font_big, getattr(state, "boss_intro_text", "") or "", maxw)
                    ty = int(HEIGHT * 0.28)
                    for line in lines:
                        txt = state.font_big.render(line, True, (255, 255, 255))
                        sh  = state.font_big.render(line, True, (0, 0, 0))
                        screen.blit(sh,  (tx + 2, ty + 2))
                        screen.blit(txt, (tx, ty))
                        ty += txt.get_height() + 6
                    # Hinweis
                    hint = state.font_hud.render("ENTER = Start", True, (255, 255, 255))
                    sh   = state.font_hud.render("ENTER = Start", True, (0, 0, 0))
                    screen.blit(sh,   (WIDTH // 2 - hint.get_width() // 2 + 2, HEIGHT - 70 + 2))
                    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2,     HEIGHT - 70))

                # ---- Angriff!!! direkt über dem Boss ----
                if getattr(state, "end_shout_t", 0.0) <= 0.0 and getattr(state, "attack_msg_t", 0.0) > 0.0 and getattr(state, "_attack_msg", None) and getattr(state, "boss", None):
                    img = state.boss.frames[state.boss.idx] if state.boss.playing else state.boss.frames[0]
                    ax, ay = state.boss.anchor
                    tlx = int(state.boss.fx - ax)
                    tly = int(state.boss.fy - ay)
                    x = tlx + img.get_width() // 2 - state._attack_msg.get_width() // 2
                    y = max(6, tly - state._attack_msg.get_height() - 8)
                    screen.blit(state._attack_msg_shadow, (x + 2, y + 2))
                    screen.blit(state._attack_msg,        (x, y))

                # ---- End-Text zentriert ----
                if getattr(state, "end_shout_t", 0.0) > 0.0 and getattr(state, "_end_msg", None):
                    cx = WIDTH // 2
                    cy = HEIGHT // 2
                    screen.blit(state._end_msg_shadow, (cx - state._end_msg_shadow.get_width() // 2 + 2, cy - 160 + 2))
                    screen.blit(state._end_msg,        (cx - state._end_msg.get_width() // 2,        cy - 160))

                # Start-Overlay (Titel + Welleninfo), nur wenn KEIN Boss-Intro gerade läuft
                if state.waiting_start and not getattr(state, "boss_intro_active", False):
                    lbl = get_level_title(world_name, levels[level_index], sublevels[sub_index][0])
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 160))
                    screen.blit(overlay, (0, 0))
                    title = state.font_big.render(lbl, True, (220, 255, 220))
                    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
                    # Welleninfo
                    if hasattr(state, "waves") and state.waves:
                        current = min(state.wave_index + 1, len(state.waves))
                        total = len(state.waves)
                        label = ""
                        try:
                            label = state.waves[state.wave_index].get("label", "") or ""
                        except Exception:
                            pass
                        wave_text = f"Welle {current}/{total}" + (f" – {label}" if label else "")
                        wave_surf = state.font_hud.render(wave_text, True, (220, 255, 220))
                        wave_sh   = state.font_hud.render(wave_text, True, (0, 0, 0))
                        y = HEIGHT // 2 - 60 + title.get_height() + 6
                        screen.blit(wave_sh, (WIDTH // 2 - wave_sh.get_width() // 2 + 2, y + 2))
                        screen.blit(wave_surf, (WIDTH // 2 - wave_surf.get_width() // 2, y))
                    hint = state.font_hud.render("Drücke ENTER, um zu starten", True, (255, 255, 255))
                    sh   = state.font_hud.render("Drücke ENTER, um zu starten", True, (0, 0, 0))
                    screen.blit(sh,   (WIDTH // 2 - sh.get_width() // 2 + 2, HEIGHT // 2 + 10 + 2))
                    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 10))

                # Level-Ende Overlay?
                if level_overlay is not None and not state.waiting_start:
                    level_overlay.draw(screen, state.font_big, state.font_hud)

                # Game Over?
                if state.game_over:
                    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    ov.fill((0, 0, 0, 160))
                    screen.blit(ov, (0, 0))
                    t = state.font_end.render("GAME OVER", True, (255, 220, 220))
                    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - t.get_height() // 2 - 30))
                    s = state.font_hud.render("ESC = Beenden • R = Neustart Level", True, (230, 230, 230))
                    screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 30))

                # Fadenkreuz-Klick
                if cross_pos and pygame.time.get_ticks() < cross_until:
                    screen.blit(cross, (int(cross_pos[0]), int(cross_pos[1])))

        # --- Pause-Overlay ---
        if world_mode == "game" and state and getattr(state, "paused", False):
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 120))
            screen.blit(ov, (0, 0))
            txt = state.font_end.render("PAUSE", True, (255, 255, 255))
            sh = state.font_end.render("PAUSE", True, (0, 0, 0))
            x = WIDTH // 2 - txt.get_width() // 2
            y = HEIGHT // 2 - txt.get_height() // 2
            screen.blit(sh, (x + 2, y + 2))
            screen.blit(txt, (x, y))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
