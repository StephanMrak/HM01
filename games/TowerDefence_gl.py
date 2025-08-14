# NOTE: This version keeps your game logic intact but swaps the renderer to OpenGL ES.
# - Uses pygame for window/input/timing/image loading/masks/fonts
# - Uses PyOpenGL to draw textured quads for background, sprites, and UI text
# - Replaces sprite Group with GLGroup that draws via GPU; `clear()` becomes a no-op
# - Your resources/paths remain the same; no file names changed
# - You can drop-in replace your original file with this one (or rename to avoid clobbering)

wall_life = 1000
points = 0


def main():
    # some colors to use
    game_lost = False
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 191, 255)
    RED = (255, 0, 0)
    HIMMELBLAU = (120, 210, 255)
    YELLOW = (255, 255, 0)
    xbackground = 0
    ybackground = 0
    iAnimation = 0
    # Variablen init
    mausx = 0
    mausy = 0
    randomx = 0
    wizard_hit = False
    wizard_count = 0
    offsetWizard = (0, 0)
    offsetKnight = (0, 0)

    import time
    import pygame
    import hmsysteme
    import math
    import random
    import os
    import sys
    import platform
    import pygame.freetype
    import pygame.locals
    import numpy as np

    from OpenGL import GL as gl
    from OpenGL.GL import shaders

    print(platform.uname())
    hmsysteme.put_button_names(["upgrade wall","upgrade weapon","start/stop"])

    # FPS tracking variables
    debug_fps = True  # hmsysteme.get_debug()
    if debug_fps:
        fps_samples = []
        frame_count = 0
        fps_update_interval = 30  # Update every 30 frames
        mean_fps_display = 0.0  # Store the mean FPS for display

    # ------------------------------
    # Pygame + OpenGL ES init
    # ------------------------------
    pygame.init()

    path = os.path.realpath(__file__)
    print(path)

    if 'Linux' in platform.uname():
        path = path.replace('TowerDefence_gl.py', '')
    else:
        path = path.replace('TowerDefence_gl.py', '')

    size = hmsysteme.get_size()

    flags = pygame.OPENGL | pygame.DOUBLEBUF
    if hmsysteme.get_debug() is True:
        screen = pygame.display.set_mode(size, flags)
    else:
        # Fullscreen + GL
        screen = pygame.display.set_mode((1366, 762), flags | pygame.FULLSCREEN)
        size = screen.get_size()

    clock = pygame.time.Clock()
    pygame.display.set_caption("Competition (OpenGL)")

    # ------------------------------
    # Simple GL renderer for textured quads
    # ------------------------------
    VERT_SHADER = """
    #version 120
    attribute vec2 aPos;      // NDC -1..1
    attribute vec2 aUV;
    varying vec2 vUV;
    void main(){
        vUV = aUV;
        gl_Position = vec4(aPos, 0.0, 1.0);
    }
    """

    FRAG_SHADER = """
    #version 120
    varying vec2 vUV;
    uniform sampler2D uTex;
    void main(){
        vec4 c = texture2D(uTex, vUV);
        gl_FragColor = c; // premultiplied not assumed; rely on standard alpha blend
    }
    """

    program = shaders.compileProgram(
        shaders.compileShader(VERT_SHADER, gl.GL_VERTEX_SHADER),
        shaders.compileShader(FRAG_SHADER, gl.GL_FRAGMENT_SHADER),
    )

    aPos_loc = gl.glGetAttribLocation(program, 'aPos')
    aUV_loc = gl.glGetAttribLocation(program, 'aUV')
    uTex_loc = gl.glGetUniformLocation(program, 'uTex')

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glDisable(gl.GL_DEPTH_TEST)

    # Dynamic VBO for a single quad per draw (we keep it simple)
    vbo = gl.glGenBuffers(1)

    def ndc_quad(x, y, w, h, screen_w, screen_h, u0=0.0, v0=0.0, u1=1.0, v1=1.0):
        # convert pixel coords top-left origin to NDC with bottom-left origin
        # pygame uses y-down; OpenGL uses y-up. We'll map so y-down works correctly.
        # We'll compute NDC positions assuming 0,0 at top-left:
        x0 = (x / screen_w) * 2.0 - 1.0
        y0 = 1.0 - (y / screen_h) * 2.0
        x1 = ((x + w) / screen_w) * 2.0 - 1.0
        y1 = 1.0 - ((y + h) / screen_h) * 2.0
        # vertices (triangle strip style):
        # (x0,y0)-(u0,v0) TL, (x1,y0)-(u1,v0) TR, (x0,y1)-(u0,v1) BL, (x1,y1)-(u1,v1) BR
        return np.array([
            x0, y0,  u0, v0,
            x1, y0,  u1, v0,
            x0, y1,  u0, v1,
            x1, y1,  u1, v1,
        ], dtype=np.float32)

    # Texture cache: map pygame.Surface object id to GL texture id
    surf_tex_cache = {}

    def surface_to_texture(surf):
        # Cache by id(surf) so reused frames don't reupload
        key = id(surf)
        if key in surf_tex_cache:
            return surf_tex_cache[key]
        w, h = surf.get_size()
        # Ensure pixel format RGBA
        rgba = pygame.image.tostring(surf, "RGBA", 0)
        tex = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, rgba)
        surf_tex_cache[key] = (tex, w, h)
        return surf_tex_cache[key]

    def update_texture(tex_tuple, surf):
        # For dynamic content (e.g., frequently changing text), reupload in-place
        tex, w, h = tex_tuple
        sw, sh = surf.get_size()
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        if (sw, sh) == (w, h):
            rgba = pygame.image.tostring(surf, "RGBA", 0)
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, rgba)
        else:
            # size changed: recreate
            rgba = pygame.image.tostring(surf, "RGBA", 0)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, sw, sh, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, rgba)
            surf_tex_cache[id(surf)] = (tex, sw, sh)
            return (tex, sw, sh)
        return tex_tuple

    def draw_surface(surf, pos, area=None):
        # area: pygame.Rect to draw sub-rect (optional)
        tex, tw, th = surface_to_texture(surf)
        x, y = pos
        if area is not None:
            ax, ay, aw, ah = area
            u0 = ax / tw
            v0 = ay / th
            u1 = (ax + aw) / tw
            v1 = (ay + ah) / th
            w, h = aw, ah
        else:
            u0, v0, u1, v1 = 0.0, 0.0, 1.0, 1.0
            w, h = tw, th

        verts = ndc_quad(x, y, w, h, size[0], size[1], u0, v0, u1, v1)
        gl.glUseProgram(program)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
        gl.glUniform1i(uTex_loc, 0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, verts.nbytes, verts, gl.GL_DYNAMIC_DRAW)
        stride = 4 * 4  # 4 floats per vertex: x,y,u,v
        gl.glEnableVertexAttribArray(aPos_loc)
        gl.glVertexAttribPointer(aPos_loc, 2, gl.GL_FLOAT, False, stride, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(aUV_loc)
        gl.glVertexAttribPointer(aUV_loc, 2, gl.GL_FLOAT, False, stride, gl.ctypes.c_void_p(8))
        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    # Minimal wrapper to mimic blit() usage in your code
    class GLScreenWrapper:
        def __init__(self):
            self.size = size
        def get_size(self):
            return self.size
        def blit(self, surf, dest, area=None):
            # dest can be (x,y) or a Rect
            if isinstance(dest, pygame.Rect):
                pos = (dest.x, dest.y)
            else:
                pos = dest
            draw_surface(surf, pos, area)
        def fill(self, color):
            r,g,b = color
            gl.glClearColor(r/255.0, g/255.0, b/255.0, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    glscreen = GLScreenWrapper()

    # ------------------------------
    # Image Loading Class (unchanged)
    # ------------------------------
    class ImageLoader:
        def __init__(self, path):
            self.path = path
            self.background_pics = []
            self.campfire_pics = []
            self.coin_pics = []
            self.knight_pics = []
            self.wizard_pics = []
            self.diabolo = None
            self.load_all_images()
            
        def load_all_images(self):
            # Load background images
            background_files = [
                "grassland.png", "grassstoneland.png", "caveentry.png", "wall1.png", "wall2.png",
                "tower1.png", "caverails.png", "wall3.png", "wall4.png", "grass1.png",
                "stone1.png", "cross1.png", "cross2.png", "cross3.png", "tombstone1.png",
                "tombstone2.png", "tombstone3.png", "grassstoneland2.png", "statue1.png", "tree_dead1.png",
                "tree_dead2.png", "tree_dead3.png", "fence_wood1.png", "fence_metal1.png", "fence_metal2.png",
                "fence_metal3.png", "fence_metal4.png", "fence_metal5.png", "grassstoneland3.png", "grassstoneland4.png",
                "grassstoneland5.png", "grass2.png", "chest1.png", "tree_snow1.png", "tree_snow2.png",
                "tree_snow3.png", "tree_snow4.png", "tree1.png", "fence_wood2.png"
            ]
            
            for filename in background_files:
                try:
                    img = pygame.image.load(os.path.join(self.path, "pics/Background/Competition", filename)).convert_alpha()
                    self.background_pics.append(img)
                except pygame.error as e:
                    print(f"Could not load {filename}: {e}")
                    placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
                    placeholder.fill((255, 0, 255, 255))
                    self.background_pics.append(placeholder)
            
            # Load campfire animation
            campfire_files = ["CampFire1.png", "CampFire1.png", "CampFire2.png", "CampFire2.png", 
                            "CampFire3.png", "CampFire3.png", "CampFire4.png", "CampFire4.png",
                            "CampFire5.png", "CampFire5.png"]
            
            for filename in campfire_files:
                try:
                    img = pygame.image.load(os.path.join(self.path, "pics/Background/Competition", filename)).convert_alpha()
                    self.campfire_pics.append(img)
                except pygame.error as e:
                    print(f"Could not load {filename}: {e}")
                    placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
                    placeholder.fill((255, 128, 0, 255))
                    self.campfire_pics.append(placeholder)
            
            # Load coin animation
            coin_files = ["coin_gold1.png", "coin_gold1.png", "coin_gold2.png", "coin_gold3.png",
                         "coin_gold4.png", "coin_gold5.png", "coin_gold6.png", "coin_gold7.png",
                         "coin_gold8.png", "coin_gold8.png"]
            
            for filename in coin_files:
                try:
                    img = pygame.image.load(os.path.join(self.path, "pics/Background/Competition", filename)).convert_alpha()
                    self.coin_pics.append(img)
                except pygame.error as e:
                    print(f"Could not load {filename}: {e}")
                    placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
                    placeholder.fill((255, 255, 0, 255))
                    self.coin_pics.append(placeholder)
            
            # Load knight animations
            knight_files = [
                "BlueKnight_entity_000_walk_000.png", "BlueKnight_entity_000_walk_001.png",
                "BlueKnight_entity_000_walk_002.png", "BlueKnight_entity_000_walk_003.png",
                "BlueKnight_entity_000_walk_004.png", "BlueKnight_entity_000_walk_005.png",
                "BlueKnight_entity_000_walk_006.png", "BlueKnight_entity_000_walk_007.png",
                "BlueKnight_entity_000_walk_008.png", "BlueKnight_entity_000_walk_009.png",
                "BlueKnight_entity_000_dead_front_000.png", "BlueKnight_entity_000_dead_front_001.png",
                "BlueKnight_entity_000_dead_front_002.png", "BlueKnight_entity_000_dead_front_003.png",
                "BlueKnight_entity_000_dead_front_004.png", "BlueKnight_entity_000_dead_front_005.png",
                "BlueKnight_entity_000_dead_front_006.png", "BlueKnight_entity_000_dead_front_007.png",
                "BlueKnight_entity_000_dead_front_008.png", "BlueKnight_entity_000_run_000.png",
                "BlueKnight_entity_000_run_001.png", "BlueKnight_entity_000_run_002.png",
                "BlueKnight_entity_000_run_003.png", "BlueKnight_entity_000_run_004.png",
                "BlueKnight_entity_000_run_005.png", "BlueKnight_entity_000_run_006.png",
                "BlueKnight_entity_000_run_007.png", "BlueKnight_entity_000_run_008.png",
                "BlueKnight_entity_000_run_009.png", "BlueKnight_entity_000_basic attack style 2_000.png",
                "BlueKnight_entity_000_basic attack style 2_001.png", "BlueKnight_entity_000_basic attack style 2_002.png",
                "BlueKnight_entity_000_basic attack style 2_003.png", "BlueKnight_entity_000_basic attack style 2_004.png",
                "BlueKnight_entity_000_basic attack style 2_005.png", "BlueKnight_entity_000_basic attack style 2_006.png",
                "BlueKnight_entity_000_basic attack style 2_007.png", "BlueKnight_entity_000_basic attack style 2_008.png",
                "BlueKnight_entity_000_basic attack style 2_009.png"
            ]
            
            for filename in knight_files:
                try:
                    img = pygame.image.load(os.path.join(self.path, "pics/Knight", filename)).convert_alpha()
                    self.knight_pics.append(img)
                except pygame.error as e:
                    print(f"Could not load {filename}: {e}")
                    placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
                    placeholder.fill((0, 0, 255, 255))
                    self.knight_pics.append(placeholder)
            
            # Load wizard images
            wizard_files = ["wizard1.png", "wizard2.png", "wizard3.png", "wizard4.png",
                           "wizard5.png", "wizard6.png", "wizard7.png", "wizard8.png"]
            
            for filename in wizard_files:
                try:
                    img = pygame.image.load(os.path.join(self.path, "pics/Wizard", filename)).convert_alpha()
                    self.wizard_pics.append(img)
                except pygame.error as e:
                    print(f"Could not load {filename}: {e}")
                    placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
                    placeholder.fill((128, 0, 128, 255))
                    self.wizard_pics.append(placeholder)
            
            # Load diabolo/shot image
            try:
                self.diabolo = pygame.image.load(os.path.join(self.path, "pics/Schuss.png")).convert_alpha()
            except pygame.error as e:
                print(f"Could not load Schuss.png: {e}")
                self.diabolo = pygame.Surface((15, 15), pygame.SRCALPHA)
                self.diabolo.fill((255, 255, 255, 255))

    # Load all images at startup
    print("Loading images...")
    image_loader = ImageLoader(path)
    print("Images loaded successfully!")

    # Create static backgrounds (same composition, but we'll draw via GL each frame)
    def create_background(background):
        for i in range(-1, 22):
            xbackground = i * 64
            for a in range(-1, 24):
                ybackground = a * 32
                background.blit(image_loader.background_pics[0], (xbackground, ybackground))
        for i in range(-1, 22):
            xbackground = i * 64 + 32
            for a in range(-1, 24):
                ybackground = a * 32 + 16
                background.blit(image_loader.background_pics[0], (xbackground, ybackground))

        # Cave / Wall
        background.blit(image_loader.background_pics[2], (100, 80))
        background.blit(image_loader.background_pics[3], (75, 113))
        background.blit(image_loader.background_pics[4], (40, 98))
        background.blit(image_loader.background_pics[7], (1, 82))
        background.blit(image_loader.background_pics[7], (-15, 82))
        background.blit(image_loader.background_pics[7], (165, 65))
        background.blit(image_loader.background_pics[3], (205, 80))
        background.blit(image_loader.background_pics[7], (230, 65))
        background.blit(image_loader.background_pics[3], (270, 80))
        background.blit(image_loader.background_pics[8], (295, 60))
        background.blit(image_loader.background_pics[8], (327, 43))
        background.blit(image_loader.background_pics[7], (360, 25))
        background.blit(image_loader.background_pics[4], (397, 40))
        background.blit(image_loader.background_pics[4], (430, 55))
        background.blit(image_loader.background_pics[3], (465, 70))
        background.blit(image_loader.background_pics[7], (490, 58))
        background.blit(image_loader.background_pics[6], (525, 70))
        background.blit(image_loader.background_pics[4], (585, 100))
        background.blit(image_loader.background_pics[3], (620, 115))
        background.blit(image_loader.background_pics[8], (645, 100))
        background.blit(image_loader.background_pics[8], (678, 83))
        background.blit(image_loader.background_pics[8], (710, 65))
        background.blit(image_loader.background_pics[8], (740, 45))
        background.blit(image_loader.background_pics[7], (770, 30))
        background.blit(image_loader.background_pics[3], (810, 45))
        background.blit(image_loader.background_pics[8], (835, 25))
        background.blit(image_loader.background_pics[8], (865, 10))
        background.blit(image_loader.background_pics[8], (895, -7))
        background.blit(image_loader.background_pics[8], (925, -25))
        background.blit(image_loader.background_pics[8], (955, -40))
        background.blit(image_loader.background_pics[8], (985, -55))
        background.blit(image_loader.background_pics[10], (620, 70))
        background.blit(image_loader.background_pics[9], (645, 45))
        background.blit(image_loader.background_pics[9], (595, 50))
        background.blit(image_loader.background_pics[9], (625, 40))

        # Trees
        background.blit(image_loader.background_pics[33], (850, -150))
        background.blit(image_loader.background_pics[34], (930, -100))
        background.blit(image_loader.background_pics[35], (1010, -50))
        background.blit(image_loader.background_pics[36], (1100, -0))
        background.blit(image_loader.background_pics[37], (1200, -30))
        background.blit(image_loader.background_pics[34], (1050, -100))
        background.blit(image_loader.background_pics[34], (1000, -180))
        background.blit(image_loader.background_pics[34], (1100, -180))
        background.blit(image_loader.background_pics[37], (1150, -130))
        background.blit(image_loader.background_pics[34], (1200, -180))
        background.blit(image_loader.background_pics[34], (300, -180))
        background.blit(image_loader.background_pics[34], (400, -150))
        background.blit(image_loader.background_pics[34], (100, -150))
        background.blit(image_loader.background_pics[34], (550, -220))
        background.blit(image_loader.background_pics[36], (50, -180))
        background.blit(image_loader.background_pics[36], (200, -180))
        background.blit(image_loader.background_pics[36], (250, -190))
        background.blit(image_loader.background_pics[36], (650, -180))

        # Tower
        background.blit(image_loader.background_pics[5], (1100, 250))
        background.blit(image_loader.background_pics[5], (1100, 550))

        # Graveyard
        background.blit(image_loader.background_pics[30], (350, 590))
        background.blit(image_loader.background_pics[30], (380, 605))
        background.blit(image_loader.background_pics[29], (580, 510))
        background.blit(image_loader.background_pics[29], (500, 490))
        background.blit(image_loader.background_pics[29], (500, 510))
        background.blit(image_loader.background_pics[29], (520, 500))
        background.blit(image_loader.background_pics[29], (550, 500))
        background.blit(image_loader.background_pics[29], (520, 520))
        background.blit(image_loader.background_pics[29], (490, 535))
        background.blit(image_loader.background_pics[29], (465, 545))
        background.blit(image_loader.background_pics[29], (435, 560))
        background.blit(image_loader.background_pics[29], (405, 575))
        background.blit(image_loader.background_pics[29], (385, 585))
        background.blit(image_loader.background_pics[23], (200, 290))
        background.blit(image_loader.background_pics[23], (250, 315))
        background.blit(image_loader.background_pics[23], (300, 340))
        background.blit(image_loader.background_pics[23], (350, 365))
        background.blit(image_loader.background_pics[23], (400, 390))
        background.blit(image_loader.background_pics[26], (450, 413))
        background.blit(image_loader.background_pics[26], (550, 460))
        background.blit(image_loader.background_pics[27], (600, 488))
        background.blit(image_loader.background_pics[25], (550, 512))
        background.blit(image_loader.background_pics[25], (500, 537))
        background.blit(image_loader.background_pics[25], (450, 562))
        background.blit(image_loader.background_pics[25], (400, 587))
        background.blit(image_loader.background_pics[25], (350, 612))
        background.blit(image_loader.background_pics[25], (300, 637))
        background.blit(image_loader.background_pics[25], (250, 662))
        background.blit(image_loader.background_pics[25], (200, 687))
        background.blit(image_loader.background_pics[25], (150, 712))
        background.blit(image_loader.background_pics[25], (100, 737))
        background.blit(image_loader.background_pics[24], (150, 270))
        background.blit(image_loader.background_pics[25], (93, 290))
        background.blit(image_loader.background_pics[25], (45, 315))
        background.blit(image_loader.background_pics[25], (-7, 341))
        background.blit(image_loader.background_pics[1], (140, 490))
        background.blit(image_loader.background_pics[1], (170, 505))
        background.blit(image_loader.background_pics[1], (200, 520))
        background.blit(image_loader.background_pics[1], (235, 535))
        background.blit(image_loader.background_pics[1], (265, 550))
        background.blit(image_loader.background_pics[1], (295, 565))
        background.blit(image_loader.background_pics[1], (330, 580))
        background.blit(image_loader.background_pics[1], (110, 505))
        background.blit(image_loader.background_pics[1], (80, 520))
        background.blit(image_loader.background_pics[1], (50, 538))
        background.blit(image_loader.background_pics[1], (18, 555))
        background.blit(image_loader.background_pics[1], (-10, 575))
        background.blit(image_loader.background_pics[1], (-45, 595))
        background.blit(image_loader.background_pics[17], (255, 495))
        background.blit(image_loader.background_pics[17], (215, 475))
        background.blit(image_loader.background_pics[14], (245, 440))
        background.blit(image_loader.background_pics[17], (170, 450))
        background.blit(image_loader.background_pics[13], (200, 370))
        background.blit(image_loader.background_pics[17], (310, 520))
        background.blit(image_loader.background_pics[17], (340, 500))
        background.blit(image_loader.background_pics[17], (340, 500))
        background.blit(image_loader.background_pics[17], (380, 500))
        background.blit(image_loader.background_pics[17], (330, 530))
        background.blit(image_loader.background_pics[17], (350, 540))
        background.blit(image_loader.background_pics[17], (390, 500))
        background.blit(image_loader.background_pics[18], (330, 410))
        background.blit(image_loader.background_pics[14], (285, 460))
        background.blit(image_loader.background_pics[15], (45, 480))
        background.blit(image_loader.background_pics[15], (0, 505))
        background.blit(image_loader.background_pics[14], (170, 550))
        background.blit(image_loader.background_pics[14], (215, 575))
        background.blit(image_loader.background_pics[14], (262, 600))
        background.blit(image_loader.background_pics[12], (90, 550))
        background.blit(image_loader.background_pics[12], (40, 580))
        background.blit(image_loader.background_pics[16], (70, 410))
        background.blit(image_loader.background_pics[19], (115, 240))
        background.blit(image_loader.background_pics[20], (290, 330))
        background.blit(image_loader.background_pics[21], (120, 380))
        background.blit(image_loader.background_pics[31], (400, 520))
        background.blit(image_loader.background_pics[9], (417, 507))
        # chest
        background.blit(image_loader.background_pics[32], (1175, 425))
        # tall grass
        background.blit(image_loader.background_pics[9], (400, 350))

        return background

    def create_wall(background):
        for i in range(-1, 22):
            xbackground = i * 64
            for a in range(-1, 24):
                ybackground = a * 32
                background.blit(image_loader.background_pics[0], (xbackground, ybackground))
        for i in range(-1, 22):
            xbackground = i * 64 + 32
            for a in range(-1, 24):
                ybackground = a * 32 + 16
                background.blit(image_loader.background_pics[0], (xbackground, ybackground))

        background.blit(image_loader.background_pics[38], (0, 0))
        background.blit(image_loader.background_pics[38], (0, 50))
        background.blit(image_loader.background_pics[38], (0, 100))
        background.blit(image_loader.background_pics[38], (0, 150))
        background.blit(image_loader.background_pics[38], (0, 200))
        background.blit(image_loader.background_pics[38], (0, 250))
        background.blit(image_loader.background_pics[38], (0, 300))
        background.blit(image_loader.background_pics[38], (0, 350))
        background.blit(image_loader.background_pics[38], (0, 400))
        background.blit(image_loader.background_pics[38], (0, 450))
        return background

    # ------------------------------
    # Sprite Classes (logic unchanged)
    # ------------------------------
    class CampfireSprite(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.images = image_loader.campfire_pics
            self.current_frame = 0
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.animation_counter = 0

        def update(self):
            self.animation_counter += 1
            if self.animation_counter >= 2:  # Change frame every 2 game ticks
                self.current_frame = (self.current_frame + 1) % len(self.images)
                self.image = self.images[self.current_frame]
                self.animation_counter = 0

    class CoinSprite(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.images = image_loader.coin_pics
            self.current_frame = 0
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.animation_counter = 0

        def update(self):
            self.animation_counter += 1
            if self.animation_counter >= 2:  # Change frame every 2 game ticks
                self.current_frame = (self.current_frame + 1) % len(self.images)
                self.image = self.images[self.current_frame]
                self.animation_counter = 0

    class WizardSprite(pygame.sprite.Sprite):
        def __init__(self, x, y, speed, xMin, xMax, yMin, yMax):
            super().__init__()
            self.images = image_loader.wizard_pics
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.speed = speed
            self.xMin = xMin
            self.xMax = xMax
            self.yMin = yMin
            self.yMax = yMax
            self.mask = pygame.mask.from_surface(self.image)
            self.hit = False
            self.counter = 0
            self.dead = False

        def update(self):
            if self.hit and not self.dead:
                if self.counter < len(self.images) - 1:
                    self.image = self.images[self.counter]
                    self.counter += 1
                else:
                    self.dead = True
            elif not self.dead:
                self.image = self.images[0]

    class KnightSprite(pygame.sprite.Sprite):
        def __init__(self, x, y, xMin, xMax, yMin, yMax):
            super().__init__()
            self.images = image_loader.knight_pics
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.xMin = xMin
            self.distance = 950
            self.xMax = xMax
            self.yMin = yMin
            self.yMax = yMax
            self.mask = pygame.mask.from_surface(self.image)
            self.hit = False
            self.counter = random.randint(0, 8)
            self.counter2 = 10
            self.counter3 = 29
            self.dead = False
            self.walking = random.randint(0, 1)
            self.speed = 0

        def revive(self):
            self.distance = 950
            self.rect.x = random.randint(200, size[0] - 800)
            self.hit = False
            self.counter = random.randint(0, 8)
            self.counter2 = 10
            self.counter3 = 29
            self.dead = False
            self.walking = random.randint(0, 1)

        def update(self):
            global points, wall_life
            if self.hit and not self.dead:
                # dying
                if self.counter2 < 18:
                    self.image = self.images[self.counter2]
                    self.counter2 += 1
                    self.speed = 0
                else:
                    self.dead = True
                    points += 5

            elif not self.dead:
                # attacking
                if self.rect.x >= self.distance:
                    self.image = self.images[self.counter3]
                    self.counter3 += 1
                    if self.counter3 > 38:
                        self.counter3 = 29
                        wall_life = wall_life - 1
                # walking
                elif self.walking:
                    self.speed = 1
                    self.rect.x += self.speed
                    self.image = self.images[self.counter]
                    self.counter += 1
                    if self.counter >= 9:
                        self.counter = 0
                # running
                else:
                    self.speed = 2
                    self.rect.x += self.speed
                    self.image = self.images[self.counter + 19]
                    self.counter += 1
                    if self.counter >= 9:
                        self.counter = 0
            # dead
            else:
                self.image = self.images[18]

    # ------------------------------
    # GL-aware Group (drop-in for pygame.sprite.Group)
    # ------------------------------
    class GLGroup(pygame.sprite.Group):
        def clear(self, surface, background):
            # no-op: we redraw the whole scene with GPU each frame
            return
        def draw(self, surface):
            # draw via GL using each sprite's current image and rect
            for spr in self.sprites():
                draw_surface(spr.image, (int(spr.rect.x), int(spr.rect.y)))

    # Create static background surfaces
    print("Creating background...")
    static_background = create_background(pygame.Surface(size, pygame.SRCALPHA))
    wall_fence = create_wall(pygame.Surface((100, 550), pygame.SRCALPHA))
    print("Background created!")

    # Pre-upload static background & wall as textures (first draw will cache anyway, but we can touch now)
    _ = surface_to_texture(static_background)
    _ = surface_to_texture(wall_fence)

    # Create sprite groups
    animated_sprites = GLGroup()

    # Create animated background elements
    campfire = CampfireSprite(1260, 315)
    coin = CoinSprite(1200, 450)
    animated_sprites.add(campfire, coin)

    # Create wizards
    Wizard_count = 0
    for i in range(Wizard_count):
        wizard = WizardSprite(random.randint(200, size[0] - 400), 
                             random.randint(200, size[1] - 200), 
                             2, 5, 1275, 5, 768)
        animated_sprites.add(wizard)

    # Create knights
    Knight_count = 50
    for i in range(Knight_count):
        knight = KnightSprite(random.randint(100, size[0] - 800),
                             random.randint(200, size[1] - 200),
                             5, 1275, 5, 768)
        animated_sprites.add(knight)

    # Store references for collision detection
    knight_sprites = [sprite for sprite in animated_sprites if isinstance(sprite, KnightSprite)]
    wizard_sprites = [sprite for sprite in animated_sprites if isinstance(sprite, WizardSprite)]

    # Create masks for collision detection
    Diabolo_Mask = pygame.mask.from_surface(image_loader.diabolo)
    Diabolo_Rect = image_loader.diabolo.get_rect(center=(50, 50))

    GAME_FONT = pygame.font.SysFont("Times", 50)

    # Game state variables
    hit_for_screenshot = False
    screenshot_delay = 0

    print("Starting game loop (OpenGL rendering)...")

    # ------------------------------
    # Game Loop
    # ------------------------------
    while hmsysteme.game_isactive():
        # Begin frame: clear
        glscreen.fill((0, 0, 0))

        # FPS tracking (if debug mode is enabled)
        if debug_fps:
            current_fps = clock.get_fps()
            fps_samples.append(current_fps)
            frame_count += 1
            if frame_count >= fps_update_interval:
                if fps_samples:
                    mean_fps_display = sum(fps_samples) / len(fps_samples)
                fps_samples = []
                frame_count = 0

        # Draw static background every frame (GPU blit)
        glscreen.blit(static_background, (0, 0))

        # Draw wall if game not lost
        if not game_lost:
            glscreen.blit(wall_fence, (1000, 200))

        # Clear animated sprites from their old positions (no-op in GL)
        animated_sprites.clear(screen, static_background)

        # Update all animated sprites
        animated_sprites.update()

        # Draw all animated sprites to screen (GPU)
        animated_sprites.draw(screen)

        # Check if all knights are dead and revive them
        all_dead = True
        for knight in knight_sprites:
            if not knight.dead:
                all_dead = False
                break
        if all_dead and len(knight_sprites) > 0:
            for knight in knight_sprites:
                knight.revive()

        # Game state logic
        if wall_life <= 0:
            game_lost = True
            text = GAME_FONT.render("DEFEAT", True, (255, 0, 0))
            for knight in knight_sprites:
                knight.distance = 1200
        else:
            text = GAME_FONT.render(str(wall_life), True, (255, 0, 0))

        # Draw UI text
        glscreen.blit(text, (1000, 150))
        points_text = GAME_FONT.render(str(points), True, (0, 255, 0))
        glscreen.blit(points_text, (200, 150))

        # Display FPS if in debug mode when updated
        if debug_fps and (frame_count == 0):
            fps_text = GAME_FONT.render(f"FPS: {mean_fps_display:.1f}", True, (255, 255, 0))
            glscreen.blit(fps_text, (50, 50))

        # Handle events
        for event in pygame.event.get():
            # Quit on [ESC] or [X]
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                hit_for_screenshot = True
                mausx = event.pos[0]
                mausy = event.pos[1]
                print("X:", mausx, "Y:", mausy)
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 10, 10)
                # Check collision with knights
                for knight in knight_sprites:
                    offsetKnight = (mausx - int(knight.rect.x), int(mausy - knight.rect.y))
                    if knight.mask.overlap(Diabolo_Mask, offsetKnight):
                        knight.hit = True
                # Check collision with wizards
                for wizard in wizard_sprites:
                    offsetWizard = (mausx - wizard.rect.x, mausy - wizard.rect.y)
                    if wizard.mask.overlap(Diabolo_Mask, offsetWizard):
                        wizard.hit = True

        # Handle external hit detection (from hmsysteme)
        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            Diabolo_Rect = pygame.Rect(pos[0] - 15, pos[1] - 15, 10, 10)
            # Check collision with knights
            for knight in knight_sprites:
                offsetKnight = (int(pos[0] - knight.rect.x), int(pos[1] - knight.rect.y))
                if knight.mask.overlap(Diabolo_Mask, offsetKnight):
                    knight.hit = True
            # Check collision with wizards  
            for wizard in wizard_sprites:
                offsetWizard = (int(pos[0] - wizard.rect.x), int(pos[1] - wizard.rect.y))
                if wizard.mask.overlap(Diabolo_Mask, offsetWizard):
                    wizard.hit = True

        # Handle screenshot logic (draw diabolo, flip, take screenshot)
        if hit_for_screenshot:
            screenshot_delay += 1
            if screenshot_delay == 10:
                glscreen.blit(image_loader.diabolo, (Diabolo_Rect.x, Diabolo_Rect.y))
                pygame.display.flip()
                start = time.time()
                hmsysteme.take_screenshot(screen)
                print("Screenshot time:", time.time() - start)
                screenshot_delay = 0
                hit_for_screenshot = False

        # End frame: swap buffers
        pygame.display.flip()
        clock.tick(30)

    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()
