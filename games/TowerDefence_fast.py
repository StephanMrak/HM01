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
    import os
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    import pygame
    import hmsysteme
    import math
    import random

    import sys
    import platform
    import pygame.freetype
    import pygame.locals
    import numpy as np
    print(platform.uname())
    hmsysteme.put_button_names(["upgrade wall","upgrade weapon","start/stop"])

    # FPS tracking variables
    debug_fps = True#hmsysteme.get_debug()  # Assume this tells us if debug mode is on
    if debug_fps:
        fps_samples = []
        frame_count = 0
        fps_update_interval = 30  # Update every 30 frames
        mean_fps_display = 0.0  # Store the mean FPS for display

    # Pygame init
    pygame.init()

    path = os.path.realpath(__file__)
    print(path)

    if 'Linux' in platform.uname():
        path = path.replace('TowerDefence_fast.py', '')
    else:
        path = path.replace('TowerDefence_fast.py', '')

    size = hmsysteme.get_size()
    if hmsysteme.get_debug()==True:
        screen = pygame.display.set_mode(size)
    else:
        screen=pygame.display.set_mode((1366, 762), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Competition")

    # Image Loading Class
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
                    # Create a placeholder surface
                    placeholder = pygame.Surface((64, 64))
                    placeholder.fill((255, 0, 255))  # Magenta placeholder
                    placeholder = placeholder.convert_alpha()
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
                    placeholder = pygame.Surface((32, 32))
                    placeholder.fill((255, 128, 0))  # Orange placeholder
                    placeholder = placeholder.convert_alpha()
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
                    placeholder = pygame.Surface((32, 32))
                    placeholder.fill((255, 255, 0))  # Yellow placeholder
                    placeholder = placeholder.convert_alpha()
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
                    placeholder = pygame.Surface((64, 64))
                    placeholder.fill((0, 0, 255))  # Blue placeholder
                    placeholder = placeholder.convert_alpha()
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
                    placeholder = pygame.Surface((64, 64))
                    placeholder.fill((128, 0, 128))  # Purple placeholder
                    placeholder = placeholder.convert_alpha()
                    self.wizard_pics.append(placeholder)
            
            # Load diabolo/shot image
            try:
                self.diabolo = pygame.image.load(os.path.join(self.path, "pics/Schuss.png")).convert_alpha()
            except pygame.error as e:
                print(f"Could not load Schuss.png: {e}")
                self.diabolo = pygame.Surface((15, 15))
                self.diabolo.fill((255, 255, 255))
                self.diabolo = self.diabolo.convert_alpha()

    # Load all images at startup
    print("Loading images...")
    image_loader = ImageLoader(path)
    print("Images loaded successfully!")

    # Create static backgrounds
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

    # Sprite Classes using pygame.sprite.Sprite
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

    # Create static background surfaces
    print("Creating background...")
    static_background = create_background(pygame.Surface(size))
    wall_fence = create_wall(pygame.Surface((100, 550)))
    print("Background created!")

    # Create sprite groups
    animated_sprites = pygame.sprite.Group()

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

    print("Starting game loop...")
    
    # Start Game Loop
    # Draw background once
    screen.blit(static_background, (0, 0))
    while hmsysteme.game_isactive():
        # FPS tracking (if debug mode is enabled)
        if debug_fps:
            # Get current FPS from the clock
            current_fps = clock.get_fps()
            fps_samples.append(current_fps)
            frame_count += 1
            
            # Every 30 frames, calculate and print mean FPS
            if frame_count >= fps_update_interval:
                if fps_samples:  # Avoid division by zero
                    mean_fps_display = sum(fps_samples) / len(fps_samples)
                
                # Reset for next measurement period
                fps_samples = []
                frame_count = 0

        # Draw wall if game not lost
        if not game_lost:
            screen.blit(wall_fence, (1000, 200))

        # Clear animated sprites from their old positions
        animated_sprites.clear(screen, static_background)

        # Update all animated sprites
        animated_sprites.update()

        # Draw all animated sprites to screen
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

        # Clear UI text areas before drawing new text
        ui_clear_rects = [
            pygame.Rect(1000, 150, 200, 60),  # Wall life text area
            pygame.Rect(200, 150, 200, 60),   # Points text area
        ]
        
        if debug_fps and frame_count == 1:  # Only clear FPS area when updating
            ui_clear_rects.append(pygame.Rect(50, 50, 150, 60))  # FPS text area
        
        for rect in ui_clear_rects:
            screen.blit(static_background, rect.topleft, rect)

        # Draw UI text
        screen.blit(text, (1000, 150))
        
        points_text = GAME_FONT.render(str(points), True, (0, 255, 0))
        screen.blit(points_text, (200, 150))

        # Display FPS if in debug mode
        if debug_fps and (frame_count == 1):
            fps_text = GAME_FONT.render(f"FPS: {mean_fps_display:.1f}", True, (255, 255, 0))
            screen.blit(fps_text, (50, 50))

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

        # Handle screenshot logic
        if hit_for_screenshot:
            screenshot_delay += 1
            if screenshot_delay == 10:
                screen.blit(image_loader.diabolo, Diabolo_Rect)
                pygame.display.flip()
                
                start = time.time()
                hmsysteme.take_screenshot(screen)
                print("Screenshot time:", time.time() - start)
                
                screenshot_delay = 0
                hit_for_screenshot = False

        # Update display
        pygame.display.flip()
        clock.tick(30)

    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()
