# Minimal Tower Defence core built for Pi Zero 2 performance.
# - Enemies are defined in pics/TowerDefence/Enemies/<Type> with walk/death (optional hit)
#   JSON atlases. Their local config.json now contains ONLY: walk_fps, death_fps, hit_fps, headshot_top.
# - Per level (Sublevel.waves.json) you set: paths, spawns, overlays and also move_speed/scale
#   via "mods" (all/type) or per spawn entry.
# - HP/Score/headshot_mul/headshot_instant_kill also come from the level JSON.
#
# Controls:
#   ENTER  - start the level / continue to next level after overlay
#   N      - (debug) skip to next sublevel/level
#   ESC    - quit
#   Mouse  - shoot
#
# Perf tips for Pi Zero 2:
# - all scaled atlases are cached per type&scale; images are only rescaled once.
# - cull enemies offscreen; hit animation pauses movement but uses same framesets.
# - effects are lightweight and bounded.

import os, re, math, json, random, pygame

# ===== Optional: HM-Systeme integration =======================================
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
    try:
        return HAS_HM and hasattr(hmsysteme, "hit_detected") and hmsysteme.hit_detected()
    except Exception:
        return False

def hm_get_pos():
    if HAS_HM and hasattr(hmsysteme, "get_pos"):
        try: return hmsysteme.get_pos()
        except Exception: pass
    return None

# ===== Global settings =========================================================
WIDTH, HEIGHT = 1366, 768
FPS = 30
ASSET_ROOT = os.path.dirname(os.path.realpath(__file__))

# Explosion tuning
EXP_DURATION = 0.9
GRAVITY      = 1300.0
MAX_SHARDS   = 24
SPARK_COUNT  = 38
FLASH_MS     = 100
SHAKE_MS     = 180
SHAKE_AMPL   = 10

# Overlays block when alpha above this
OVERLAY_BLOCK_ALPHA = 20  # 0..255

# ===== Helper utilities ========================================================
def try_load(path):
    try: return pygame.image.load(path).convert_alpha()
    except Exception: return None

def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def load_json_relaxed(path):
    """Allow // and /**/ comments and trailing commas in JSON files."""
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)   # block comments
    s = re.sub(r"//.*?$", "", s, flags=re.M)      # line comments
    s = re.sub(r",\s*([}\]])", r"\1", s)          # trailing commas
    return json.loads(s)

def _compute_anchors(frames_by_dir):
    """Anchor per direction = lower center of bounding area (frame 0)."""
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
    """Load a grid atlas (frames_per_dir × dirs rows). Supports frame/spacing/margin."""
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
    """Create a simple atlas from a hit.png using walk atlas dimensions."""
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
            frames[d].append(img); masks[d].append(pygame.mask.from_surface(img))
    anchors = _compute_anchors(frames)
    return {"frames":frames,"masks":masks,"fw":fw,"fh":fh,"dirs":dirs,"anchors":anchors}

# ---- Level paths / waves ------------------------------------------------------
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

# ===== Text helper =============================================================
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

# ===== Power up FX =============================================================
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

# ===== Explosion Effect ========================================================
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

# ===== Gameplay/config defaults ===============================================
def read_global_enemy_cfg():
    """Optional: global per-type overrides (frames/headshot_top only)."""
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/Enemies/config.json")
    if os.path.isfile(p):
        try: return load_json_relaxed(p)
        except Exception as e: print("[WARN] Enemies/config.json fehlerhaft:", e)
    return {}

def read_gameplay_cfg():
    """Global gameplay defaults (fallbacks for levels)."""
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence/gameplay.json")
    cfg = {
        "base_firepower": 1,
        "upgrade_threshold": 50,
        "upgrade_amount": 1,
        "max_firepower": 10,
        "default_hp": 3,
        "default_score": 10,
        "default_headshot_mul": 2.0,
        "default_speed": 95.0,   # NEW: speed fallback
        "default_scale": 1.0     # NEW: scale fallback
    }
    if os.path.isfile(p):
        try: cfg.update(load_json_relaxed(p))
        except Exception as e: print("[WARN] gameplay.json fehlerhaft:", e)
    return cfg

# ===== EnemyType and Enemy =====================================================
class EnemyType:
    """Loads atlases. Local config.json now ONLY: fps + headshot_top. scale/speed from level."""
    def __init__(self, name, folder, global_cfg):
        self.name = name
        base = name.lower()
        walk_json  = os.path.join(folder, f"{base}_walk.json")
        death_json = os.path.join(folder, f"{base}_death.json")
        self.walk  = load_grid_atlas(walk_json,  folder, fallbacks=("zWalk.png",))
        self.death = load_grid_atlas(death_json, folder, fallbacks=("zDeath.png",))

        # optional: hit
        self.hit = None
        hit_json = os.path.join(folder, f"{base}_hit.json")
        hit_img  = os.path.join(folder, "hit.png")
        if os.path.isfile(hit_json):
            try: self.hit = load_grid_atlas(hit_json, folder, fallbacks=("hit.png",))
            except Exception as e: print(f"[WARN] {name}: hit-json konnte nicht geladen werden: {e}")
        elif os.path.isfile(hit_img):
            sheet = try_load(hit_img)
            if sheet:
                self.hit = atlas_from_sheet_like_walk(sheet, self.walk)

        # local cfg
        cfg = {}
        local_cfg_path = os.path.join(folder, "config.json")
        if os.path.isfile(local_cfg_path):
            try: cfg = load_json_relaxed(local_cfg_path)
            except Exception as e: print(f"[WARN] {name}/config.json fehlerhaft: {e}")
        cfg = {**(global_cfg.get(name, {})), **cfg}

        self.walk_fps     = float(cfg.get("walk_fps", 10.0))
        self.hit_fps      = float(cfg.get("hit_fps", 10.0))
        self.death_fps    = int(cfg.get("death_fps", 12))
        self.headshot_top = float(cfg.get("headshot_top", 0.22))

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
                 hp, score, headshot_mul=2.0, headshot_instant_kill=False,
                 speed=95.0, scale=1.0):
        self.etype = etype
        scaled = etype.get_scaled(scale)
        self.frames = scaled["walk"]["frames"]
        self.masks  = scaled["walk"]["masks"]
        self.death  = scaled["death"]["frames"]
        self.hit_frames = scaled["hit"]["frames"] if scaled["hit"] else None
        self.walk_anchor  = scaled["walk"]["anchors"]
        self.death_anchor = scaled["death"]["anchors"]
        self.hit_anchor   = scaled["hit"]["anchors"] if scaled["hit"] else None

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
        # Hit animation pauses movement
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
        screen.blit(frm,(tlx,tly))

    def _local_hit_pos(self, mx,my):
        frm = self.frames[self.dir][self.findex]
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

# ===== Level load: paths, spawns, overlays, mods ==============================
def load_level_spec(level_folder, subname, enemies_dict):
    def cand(name):
        return os.path.join(ASSET_ROOT,"pics/TowerDefence",level_folder,f"{name}.waves.json")
    path = None
    for nm in (subname,
               subname.lower().replace("burma","bruma").title() if "burma" in subname.lower() else subname,
               subname.lower().replace("bruma","burma").title() if "bruma" in subname.lower() else subname):
        p = cand(nm)
        if os.path.isfile(p): path = p; break

    if not path:
        base = {"0":[(340,700),(900,170)]} if (level_folder.lower()=="level1" and subname.lower().startswith(("burma","bruma"))) \
               else {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}
        return base, [], [], {}

    try:
        data = load_json_relaxed(path)
    except Exception as e:
        print("[WARN] waves.json fehlerhaft:", e)
        return {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}, [], [], {}

    raw = _normalize_paths_struct(data) or {"0":[(100,HEIGHT-60),(WIDTH-100,60)]}
    raw = {k:_dedupe_close_points(v, 0.5) for k,v in raw.items()}
    paths = {str(k).lower(): v for k,v in raw.items()}

    spawns = data.get("spawns") or []
    mods   = data.get("mods") or {}

    q=[]
    for s in spawns:
        if not isinstance(s, dict): continue
        typ = s.get("type","Zombie")
        if typ not in enemies_dict:
            print(f"[WARN] Unbekannter Gegnertyp '{typ}' in waves."); continue
        key = str(s.get("path","0")).lower()
        if key not in paths:
            print(f"[WARN] Spawn-Pfad '{s.get('path')}' nicht gefunden. Nutze ersten verfügbaren.")
            key = next(iter(paths.keys()))
        entry = {"t": float(s.get("t",0)), "type": typ, "path": key}
        if "id" in s: entry["id"] = str(s["id"])
        # copy optional fields; defaults/overrides handled later
        for fld in ("hp","hp_mul","score","score_mul","headshot_mul","headshot_instant_kill",
                    "move_speed","scale"):
            if fld in s: entry[fld] = s[fld]
        cnt = int(s.get("count",1)); iv=float(s.get("interval",0))
        for i in range(cnt):
            e2 = dict(entry); e2["t"] = entry["t"] + i*iv
            q.append(e2)
    q.sort(key=lambda x:x["t"])

    overlay_rules=[]
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

    return paths, q, overlay_rules, mods

# ===== Overlays load (with matching rules) ====================================
def load_overlays(level_folder, subname, overlay_rules):
    folder = os.path.join(ASSET_ROOT, "pics/TowerDefence", level_folder)
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

# ===== Level end overlay =======================================================
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

# ===== Level State =============================================================
class LevelState:
    def __init__(self, bg, paths_dict, enemy_types, gameplay_cfg, spawn_queue, overlays, mods):
        self.bg = bg
        self.paths = paths_dict
        self.enemy_types = enemy_types
        self.enemies = []
        self.effects = []
        self.floaters = []
        self.power_fx = []
        self.overlays = overlays
        self.spawn_queue = list(spawn_queue)
        self.time = 0.0

        # Start gating
        self.waiting_start = True

        # Gameplay
        self.gameplay_cfg = gameplay_cfg
        self.mods = mods if isinstance(mods, dict) else {}

        self.firepower = int(gameplay_cfg.get("base_firepower",1))
        self.upgrade_threshold = int(gameplay_cfg.get("upgrade_threshold",50))
        self.upgrade_amount = int(gameplay_cfg.get("upgrade_amount",1))
        self.max_firepower = int(gameplay_cfg.get("max_firepower",10))
        self.score = 0
        self.next_upgrade_at = self.upgrade_threshold
        self.kills = 0

        self.escapes = 0
        self.max_escapes = 3
        self.game_over = False

        # Fonts
        self.font_hud     = pygame.font.SysFont(None, 30, bold=False)
        self.font_floater = pygame.font.SysFont(None, 48, bold=True)
        self.font_debug   = pygame.font.SysFont(None, 24, bold=False)
        self.font_big     = pygame.font.SysFont(None, 56, bold=True)
        self.font_end     = pygame.font.SysFont(None, 72, bold=True)

        self.last_click = None

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
        xi, yi = int(x), int(y)
        if not (0 <= xi < WIDTH and 0 <= yi < HEIGHT):
            return False
        for ov in self.overlays:
            if not ov["active"] or not ov.get("blocks", True): continue
            a = ov["surf"].get_at((xi, yi)).a
            if a > OVERLAY_BLOCK_ALPHA:
                return True
        return False

    def apply_hit(self, mx, my):
        if self.game_over or self.waiting_start:
            return False
        if self.overlay_blocks_at(mx, my):
            return False
        for e in reversed(self.enemies):
            if e.dead: continue
            kind = e.hit_kind(mx,my)
            if kind == "none": continue
            damage = max(1, self.firepower)
            if kind == "head":
                if e.headshot_instant_kill:
                    e.hp = 0
                else:
                    damage = max(1, int(round(damage * e.headshot_mul)))
            if e.hp > 0: e.hp -= damage
            if e.hp <= 0:
                frm = e.frames[e.dir][e.findex]
                self.spawn_floater(f"+{e.score}", e.fx, e.fy, frm, e.walk_anchor[e.dir])
                self.effects.append(ExplosionEffect(
                    e.death[e.dir], (int(e.fx),int(e.fy)),
                    frm, e.death_anchor[e.dir],
                    death_fps=e.etype.death_fps))
                e.dead=True
                self.kills += 1
                self.score += e.score
                self._maybe_upgrade()
            else:
                if e.hit_frames:
                    e.hit_active = True; e.hit_index = 0; e.hit_anim_accum = 0.0
            return True
        return False

    def update_spawning(self, dt):
        if self.game_over or self.waiting_start:
            return
        self.time += dt

        while self.spawn_queue and self.spawn_queue[0]["t"] <= self.time:
            s = self.spawn_queue.pop(0)

            typ = s.get("type", "Zombie")
            path_key = str(s.get("path", "0")).lower()
            path_pts = self.paths.get(path_key) or next(iter(self.paths.values()))

            # --- Level-/Typ-Modifikatoren aus waves.json
            lvl_all = self.mods.get(typ="all") if False else self.mods.get("all", {})
            lvl_typ = self.mods.get(typ, {})

            def pget(field, default=None):
                v = s.get(field, None)
                if v is None: v = lvl_typ.get(field, None)
                if v is None: v = lvl_all.get(field, None)
                return default if v is None else v

            # ---- HP (Basis + *alle* Multiplikatoren)
            hp_base = int(pget("hp", self.gameplay_cfg.get("default_hp", 3)))
            hp_mul_total = 1.0
            for v in (lvl_all.get("hp_mul"), lvl_typ.get("hp_mul"), s.get("hp_mul")):
                if v is not None:
                    try:
                        hp_mul_total *= float(v)
                    except:
                        pass
            hp = int(max(0, round(hp_base * hp_mul_total)))

            # ---- Score (Basis + *alle* Multiplikatoren)
            score_base = int(pget("score", self.gameplay_cfg.get("default_score", 10)))
            score_mul_total = 1.0
            for v in (lvl_all.get("score_mul"), lvl_typ.get("score_mul"), s.get("score_mul")):
                if v is not None:
                    try:
                        score_mul_total *= float(v)
                    except:
                        pass
            score = int(max(0, round(score_base * score_mul_total)))

            # ---- Scale/Speed aus Level (mit Gameplay-Fallback)
            scale = float(pget("scale", self.gameplay_cfg.get("default_scale", 1.0)))
            speed = float(pget("move_speed", self.gameplay_cfg.get("default_speed", 95.0)))

            # ---- Headshot-Logik pro Level (inkl. mods)
            hmul = float(pget("headshot_mul", self.gameplay_cfg.get("default_headshot_mul", 2.0)))
            hkill = bool(pget("headshot_instant_kill", False))

            enemy = Enemy(self.enemy_types[typ], path_pts,
                          hp=hp, score=score,
                          headshot_mul=hmul, headshot_instant_kill=hkill,
                          speed=speed, scale=scale)
            enemy.spawn_id = s.get("id")
            self.enemies.append(enemy)

    def update_overlay_triggers(self):
        for ov in self.overlays:
            tr = ov.get("trigger")
            if not tr or ov["active"]:
                continue
            tx, ty, r = tr["x"], tr["y"], tr["r"]
            r2 = r*r
            for e in self.enemies:
                if e.dead: continue
                if ov.get("only_type") and e.etype.name != ov["only_type"]:
                    continue
                if ov.get("only_spawn_id") and e.spawn_id != ov["only_spawn_id"]:
                    continue
                dx = e.fx - tx; dy = e.fy - ty
                if dx*dx + dy*dy <= r2:
                    ov["active"] = True
                    break

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

# ===== Main ===================================================================
def discover_sublevels(level_folder):
    p = os.path.join(ASSET_ROOT, "pics/TowerDefence", level_folder)
    if not os.path.isdir(p): return []
    imgs = []
    for f in os.listdir(p):
        lf = f.lower()
        if not lf.endswith(".png"): continue
        if lf.startswith("overlay") or ".overlay" in lf: continue
        imgs.append(f)
    imgs.sort(key=natural_key)
    return [(os.path.splitext(f)[0], os.path.join(p, f)) for f in imgs]

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

    # Load enemies
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

    # Level structure
    levels = [f"Level{i}" for i in range(1,51) if discover_sublevels(f"Level{i}")]
    if not levels: raise SystemExit("Keine Levelordner mit PNGs gefunden.")
    level_index = 0
    sublevels = discover_sublevels(levels[level_index])
    sub_index = 0

    def build_state(level_folder, subname, img_path):
        bg = try_load(img_path)
        if bg is None:
            bg = pygame.Surface((WIDTH, HEIGHT)); bg.fill((40, 60, 40))
        else:
            bg = pygame.transform.smoothscale(bg,(WIDTH,HEIGHT))
        paths_dict, spawn_q, overlay_rules, mods = load_level_spec(level_folder, subname, ENEMY_TYPES)
        overlays = load_overlays(level_folder, subname, overlay_rules)
        return LevelState(bg, paths_dict, ENEMY_TYPES, gameplay_cfg, spawn_q, overlays, mods)

    def label_for(level_i, subs, sub_i):
        lvl = levels[level_i]; name = subs[sub_i][0]
        return f"{lvl} — {name}"

    def find_next_tuple(level_i, subs, sub_i):
        nxt_li = level_i
        nxt_subs = subs
        nxt_si = sub_i + 1
        if nxt_si >= len(subs):
            nxt_li = level_i + 1
            if nxt_li >= len(levels):
                return None
            nxt_subs = discover_sublevels(levels[nxt_li])
            nxt_si = 0
        label = label_for(nxt_li, nxt_subs, nxt_si)
        return (nxt_li, nxt_subs, nxt_si, label)

    subname, img_path = sublevels[sub_index]
    state = build_state(levels[level_index], subname, img_path)

    level_overlay = None
    pending_next = None

    # Crosshair
    cross = pygame.Surface((22,22), pygame.SRCALPHA)
    pygame.draw.circle(cross,(255,255,255),(11,11),10,1)
    pygame.draw.line(cross,(255,255,255),(0,11),(22,11),1)
    pygame.draw.line(cross,(255,255,255),(11,0),(11,22),1)
    cross_pos=None; cross_until=0

    def draw_start_overlay(label):
        overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,160)); screen.blit(overlay,(0,0))
        title = state.font_big.render(label, True, (220,255,220))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
        hint  = state.font_hud.render("Drücke ENTER, um zu starten", True, (255,255,255))
        sh    = state.font_hud.render("Drücke ENTER, um zu starten", True, (0,0,0))
        screen.blit(sh,   (WIDTH//2 - sh.get_width()//2 + 2, HEIGHT//2 + 10 + 2))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2,    HEIGHT//2 + 10))

    running=True
    while running and hm_game_active():
        dt = clock.tick(FPS)/1000.0

        if not state.game_over and level_overlay is None:
            state.update_spawning(dt)
            for e in state.enemies: e.update(dt)
            state.update_overlay_triggers()

        # Cull enemies (escaped offscreen)
        if level_overlay is None and not state.waiting_start:
            pruned = []
            for e in state.enemies:
                if e.dead: continue
                at_end = (e.seg >= len(e.path) - 1)
                if at_end and (e.is_offscreen(margin=12) or e.feet_offscreen(margin=2)):
                    state.escapes += 1
                    continue
                pruned.append(e)
            state.enemies = pruned

        if not state.game_over and state.escapes > state.max_escapes:
            state.game_over = True

        # Effects/Floater/PowerFx
        for eff in list(state.effects):
            eff.update(dt)
            if eff.finished(): state.effects.remove(eff)
        for ft in list(state.floaters):
            ft.update(dt)
            if ft.finished(): state.floaters.remove(ft)
        for pfx in list(state.power_fx):
            pfx.update(dt)
            if pfx.finished(): state.power_fx.remove(pfx)

        # Input
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            elif ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: running=False
                elif ev.key==pygame.K_RETURN:
                    if state.waiting_start:
                        state.waiting_start = False
                    elif level_overlay is not None:
                        if pending_next:
                            level_index, sublevels, sub_index, _ = pending_next
                            subname, img_path = sublevels[sub_index]
                            state = build_state(levels[level_index], subname, img_path)
                        level_overlay = None; pending_next = None
                elif ev.key == pygame.K_n:  # Debug next level/sublevel
                    nxt = find_next_tuple(level_index, sublevels, sub_index)
                    if nxt is None:
                        level_index = 0; sublevels = discover_sublevels(levels[level_index]); sub_index = 0
                    else:
                        level_index, sublevels, sub_index, _ = nxt
                    subname, img_path = sublevels[sub_index]
                    state = build_state(levels[level_index], subname, img_path)
                elif state.game_over and ev.key == pygame.K_r:
                    state = build_state(levels[level_index], subname, img_path)
                    level_overlay = None; pending_next = None
            elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and not state.game_over and level_overlay is None:
                mx,my = ev.pos
                state.last_click = (mx,my)
                cross_pos = (mx - cross.get_width()//2, my - cross.get_height()//2)
                cross_until = pygame.time.get_ticks() + 120
                state.apply_hit(mx,my)

        if not state.game_over and level_overlay is None and not state.waiting_start and hm_hit_detected():
            pos = hm_get_pos()
            if pos:
                mx,my = pos
                state.last_click = (mx,my)
                cross_pos = (mx - cross.get_width()//2, my - cross.get_height()//2)
                cross_until = pygame.time.get_ticks() + 120
                state.apply_hit(mx,my)

        # Finish level overlay
        if not state.game_over and level_overlay is None and not state.waiting_start:
            alive = [e for e in state.enemies if not e.dead]
            if not state.spawn_queue and not alive and not state.effects:
                nxt = find_next_tuple(level_index, sublevels, sub_index)
                stats = {"firepower": state.firepower, "score": state.score,
                         "kills": state.kills, "escapes": state.escapes, "max_escapes": state.max_escapes}
                if nxt is not None:
                    pending_next = nxt; level_overlay = LevelEndOverlay(stats, nxt[3])
                else:
                    pending_next = None; level_overlay = LevelEndOverlay(stats, "Ende")

        # Render
        screen.blit(state.bg,(0,0))
        for e in state.enemies: e.draw(screen)
        for eff in state.effects: eff.draw(screen)
        for ov in state.overlays:
            if ov["active"]:
                screen.blit(ov["surf"], (0,0))
        for ft in state.floaters: ft.draw(screen)
        for pfx in state.power_fx: pfx.draw(screen, state.font_big)
        state.draw_hud(screen)

        if state.waiting_start:
            draw_start_overlay(label_for(level_index, sublevels, sub_index))
        if level_overlay is not None and not state.waiting_start:
            level_overlay.draw(screen, state.font_big, state.font_hud)

        if state.game_over:
            overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160)); screen.blit(overlay,(0,0))
            t = state.font_end.render("GAME OVER", True, (255,220,220))
            screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - t.get_height()//2 - 30))
            s = state.font_hud.render("ESC = Beenden • R = Neustart Level", True, (230,230,230))
            screen.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 + 30))

        if cross_pos and pygame.time.get_ticks() < cross_until:
            screen.blit(cross, (int(cross_pos[0]), int(cross_pos[1])))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()