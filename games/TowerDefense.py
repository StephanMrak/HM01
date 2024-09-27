
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
    print(platform.uname())
    hmsysteme.put_button_names(["upgrade wall","upgrade weapon","start/stop"])


    # Pygame init
    pygame.init()

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    size = hmsysteme.get_size()
    #size = hmsysteme.get_size()
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    #names = hmsysteme.get_playernames()
    names = ["Günther", "Herbert", "Dieter"]

    path = os.path.realpath(__file__)
    print(path)

    if 'Linux' in platform.uname():
        path = path.replace('TowerDefense.py', '')
    else:
        path = path.replace('TowerDefense.py', '')


    #path = r"C:/Users/flori/Dropbox/Telespiel/Raspi_Programme/HM01_v0.1/"
    if hmsysteme.check_ifdebug():
        screen = pygame.display.set_mode(size)
    else:
        screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Competition")

    #Bilder
    pic_background = [pygame.image.load(os.path.join(path,"pics/Background/Competition/grassland.png")),  #0
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/grassstoneland.png")),  #1
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/caveentry.png")),  #2
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/wall1.png")),  #3
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/wall2.png")),  #4
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/tower1.png")),  #5
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/caverails.png")),  #6
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/wall3.png")),  #7
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/wall4.png")),  #8
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/grass1.png")),  #9
                      pygame.image.load(os.path.join(path,"pics/Background/Competition/stone1.png")),  #10
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/cross1.png")),  #11
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/cross2.png")),  #12
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/cross3.png")),  #13
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tombstone1.png")),  #14
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tombstone2.png")),  #15
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tombstone3.png")),  #16
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/grassstoneland2.png")),  #17
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/statue1.png")),  #18
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree_dead1.png")),  #19
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree_dead2.png")),  #20
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree_dead3.png")),  # 21
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/fence_wood1.png")),  # 22
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/fence_metal1.png")),  # 23
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/fence_metal2.png")),  # 24
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/fence_metal3.png")),  # 25
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/fence_metal4.png")),  # 26
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/fence_metal5.png")),  # 27
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/grassstoneland3.png")),  # 28
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/grassstoneland4.png")),  # 29
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/grassstoneland5.png")),  # 30
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/grass2.png")),  # 31
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/chest1.png")),  # 32
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree_snow1.png")),  # 33
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree_snow2.png")),  # 34
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree_snow3.png")),  # 35
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree_snow4.png")),  # 36
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/tree1.png")),  # 37
                      pygame.image.load(os.path.join(path, "pics/Background/Competition/fence_wood2.png"))]  # 38]

    pic_campfire = [pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire1.png")),  #0
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire1.png")),  #1
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire2.png")),  #2
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire2.png")),  #3
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire3.png")),  #4
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/CampFire3.png")), #5
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/CampFire4.png")), #6
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/CampFire4.png")), #7
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/CampFire5.png")), #8
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/CampFire5.png"))] #9

    pic_coin =      [pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold1.png")),  #0
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold1.png")),  #1
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold2.png")),  #2
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold3.png")),  #3
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold4.png")),  #4
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold5.png")), #5
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold6.png")), #6
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold7.png")), #7
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold8.png")), #8
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold8.png"))]#9

    pic_knight=    [pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_000.png")), #0
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_001.png")),  #1
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_002.png")),  #2
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_003.png")),  #3
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_004.png")),  #4
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_005.png")),  #5
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_006.png")),  #6
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_007.png")), #7
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_008.png")),  #8
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_walk_009.png")),  #9
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_000.png")),#10
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_001.png")),#11
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_002.png")),#12
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_003.png")),#13
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_004.png")),#14
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_005.png")),#15
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_006.png")),#16
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_007.png")),#17
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_dead_front_008.png")), #18
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_000.png")), #19
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_001.png")),  #20
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_002.png")),  #21
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_003.png")),  #22
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_004.png")),  #23
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_005.png")),  #24
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_006.png")),  #25
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_007.png")), #26
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_008.png")),  #27
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_run_009.png")),  #28
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_000.png")),  #29
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_001.png")),  #30
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_002.png")), #31
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_003.png")), #32
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_004.png")), #33
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_005.png")), #34
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_006.png")), #35
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_007.png")), #36
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_008.png")), #37
                    pygame.image.load(os.path.join(path,"pics/Knight/BlueKnight_entity_000_basic attack style 2_009.png"))]  #38


    pic_Wizard = [pygame.image.load(os.path.join(path,"pics/Wizard/wizard1.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard2.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard3.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard4.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard5.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard6.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard7.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard8.png"))]


    def create_background(background):
        for i in range(-1, 22):
            xbackground = i * 64
            for a in range(-1, 24):
                ybackground = a * 32
                background.blit(pic_background[0], (xbackground, ybackground))
        for i in range(-1, 22):
            xbackground = i * 64 + 32
            for a in range(-1, 24):
                ybackground = a * 32 + 16
                background.blit(pic_background[0], (xbackground, ybackground))

        # Cave / Wall
        background.blit(pic_background[2], (100, 80))
        background.blit(pic_background[3], (75, 113))
        background.blit(pic_background[4], (40, 98))
        background.blit(pic_background[7], (1, 82))
        background.blit(pic_background[7], (-15, 82))
        background.blit(pic_background[7], (165, 65))
        background.blit(pic_background[3], (205, 80))
        background.blit(pic_background[7], (230, 65))
        background.blit(pic_background[3], (270, 80))
        background.blit(pic_background[8], (295, 60))
        background.blit(pic_background[8], (327, 43))
        background.blit(pic_background[7], (360, 25))
        background.blit(pic_background[4], (397, 40))
        background.blit(pic_background[4], (430, 55))
        background.blit(pic_background[3], (465, 70))
        background.blit(pic_background[7], (490, 58))
        background.blit(pic_background[6], (525, 70))
        background.blit(pic_background[4], (585, 100))
        background.blit(pic_background[3], (620, 115))
        background.blit(pic_background[8], (645, 100))
        background.blit(pic_background[8], (678, 83))
        background.blit(pic_background[8], (710, 65))
        background.blit(pic_background[8], (740, 45))
        background.blit(pic_background[7], (770, 30))
        background.blit(pic_background[3], (810, 45))
        background.blit(pic_background[8], (835, 25))
        background.blit(pic_background[8], (865, 10))
        background.blit(pic_background[8], (895, -7))
        background.blit(pic_background[8], (925, -25))
        background.blit(pic_background[8], (955, -40))
        background.blit(pic_background[8], (985, -55))
        background.blit(pic_background[10], (620, 70))
        background.blit(pic_background[9], (645, 45))
        background.blit(pic_background[9], (595, 50))
        background.blit(pic_background[9], (625, 40))

        # Trees
        background.blit(pic_background[33], (850, -150))
        background.blit(pic_background[34], (930, -100))
        background.blit(pic_background[35], (1010, -50))
        background.blit(pic_background[36], (1100, -0))
        background.blit(pic_background[37], (1200, -30))
        background.blit(pic_background[34], (1050, -100))
        background.blit(pic_background[34], (1000, -180))
        background.blit(pic_background[34], (1100, -180))
        background.blit(pic_background[37], (1150, -130))
        background.blit(pic_background[34], (1200, -180))
        background.blit(pic_background[34], (300, -180))
        background.blit(pic_background[34], (400, -150))
        background.blit(pic_background[34], (100, -150))
        background.blit(pic_background[34], (550, -220))
        background.blit(pic_background[36], (50, -180))
        background.blit(pic_background[36], (200, -180))
        background.blit(pic_background[36], (250, -190))
        background.blit(pic_background[36], (650, -180))


        # Tower
        background.blit(pic_background[5], (1100, 250))
        background.blit(pic_background[5], (1100, 550))

        # Graveyard
        background.blit(pic_background[30], (350, 590))
        background.blit(pic_background[30], (380, 605))
        background.blit(pic_background[29], (580, 510))
        background.blit(pic_background[29], (500, 490))
        background.blit(pic_background[29], (500, 510))
        background.blit(pic_background[29], (520, 500))
        background.blit(pic_background[29], (550, 500))
        background.blit(pic_background[29], (520, 520))
        background.blit(pic_background[29], (490, 535))
        background.blit(pic_background[29], (465, 545))
        background.blit(pic_background[29], (435, 560))
        background.blit(pic_background[29], (405, 575))
        background.blit(pic_background[29], (385, 585))
        background.blit(pic_background[23], (200, 290))
        background.blit(pic_background[23], (250, 315))
        background.blit(pic_background[23], (300, 340))
        background.blit(pic_background[23], (350, 365))
        background.blit(pic_background[23], (400, 390))
        background.blit(pic_background[26], (450, 413))
        background.blit(pic_background[26], (550, 460))
        background.blit(pic_background[27], (600, 488))
        background.blit(pic_background[25], (550, 512))
        background.blit(pic_background[25], (500, 537))
        background.blit(pic_background[25], (450, 562))
        background.blit(pic_background[25], (400, 587))
        background.blit(pic_background[25], (350, 612))
        background.blit(pic_background[25], (300, 637))
        background.blit(pic_background[25], (250, 662))
        background.blit(pic_background[25], (200, 687))
        background.blit(pic_background[25], (150, 712))
        background.blit(pic_background[25], (100, 737))
        background.blit(pic_background[24], (150, 270))
        background.blit(pic_background[25], (93, 290))
        background.blit(pic_background[25], (45, 315))
        background.blit(pic_background[25], (-7, 341))
        background.blit(pic_background[1], (140, 490))
        background.blit(pic_background[1], (170, 505))
        background.blit(pic_background[1], (200, 520))
        background.blit(pic_background[1], (235, 535))
        background.blit(pic_background[1], (265, 550))
        background.blit(pic_background[1], (295, 565))
        background.blit(pic_background[1], (330, 580))
        background.blit(pic_background[1], (110, 505))
        background.blit(pic_background[1], (80, 520))
        background.blit(pic_background[1], (50, 538))
        background.blit(pic_background[1], (18, 555))
        background.blit(pic_background[1], (-10, 575))
        background.blit(pic_background[1], (-45, 595))
        background.blit(pic_background[17], (255, 495))
        background.blit(pic_background[17], (215, 475))
        background.blit(pic_background[14], (245, 440))
        background.blit(pic_background[17], (170, 450))
        background.blit(pic_background[13], (200, 370))
        background.blit(pic_background[17], (310, 520))
        background.blit(pic_background[17], (340, 500))
        background.blit(pic_background[17], (340, 500))
        background.blit(pic_background[17], (380, 500))
        background.blit(pic_background[17], (330, 530))
        background.blit(pic_background[17], (350, 540))
        background.blit(pic_background[17], (390, 500))
        background.blit(pic_background[18], (330, 410))
        background.blit(pic_background[14], (285, 460))
        background.blit(pic_background[15], (45, 480))
        background.blit(pic_background[15], (0, 505))
        background.blit(pic_background[14], (170, 550))
        background.blit(pic_background[14], (215, 575))
        background.blit(pic_background[14], (262, 600))
        background.blit(pic_background[12], (90, 550))
        background.blit(pic_background[12], (40, 580))
        background.blit(pic_background[16], (70, 410))
        background.blit(pic_background[19], (115, 240))
        background.blit(pic_background[20], (290, 330))
        background.blit(pic_background[21], (120, 380))
        background.blit(pic_background[31], (400, 520))
        background.blit(pic_background[9], (417, 507))
        #chest
        background.blit(pic_background[32], (1175, 425))
        #wood fence

        #tall grass

        background.blit(pic_background[9], (400, 350))

        return background

    def create_wall(background):
        for i in range(-1, 22):
            xbackground = i * 64
            for a in range(-1, 24):
                ybackground = a * 32
                background.blit(pic_background[0], (xbackground, ybackground))
        for i in range(-1, 22):
            xbackground = i * 64 + 32
            for a in range(-1, 24):
                ybackground = a * 32 + 16
                background.blit(pic_background[0], (xbackground, ybackground))

        background.blit(pic_background[38], (0, 0))
        background.blit(pic_background[38], (0, 50))
        background.blit(pic_background[38], (0, 100))
        background.blit(pic_background[38], (0, 150))
        background.blit(pic_background[38], (0, 200))
        background.blit(pic_background[38], (0, 250))
        background.blit(pic_background[38], (0, 300))
        background.blit(pic_background[38], (0, 350))
        background.blit(pic_background[38], (0, 400))
        background.blit(pic_background[38], (0, 450))
        return background



    class Player:
        def __init__(self, name, score, inturn):
            self.name = name
            self.score = score
            self.inturn = inturn



    class Wizard:
        def __init__(self, x, y, speed, xMin, xMax, yMin, yMax, pics, mask, hit):
            self.x = x
            self.y = y
            self.speed = speed
            self.xMin = xMin
            self.xMax = xMax
            self.yMin = yMin
            self.yMax = yMax
            self.pics= pics
            self.mask = mask
            self.hit = hit
            self.counter=0
            self.dead=False

        def draw(self):
            if self.hit and not self.dead:
                screen.blit(self.pics[self.counter], (self.x, self.y))
                self.counter+=1
                if self.counter==7:
                    self.dead=True
                    #self.counter=0
                    #self.hit=False
            elif not self.dead:
                screen.blit(self.pics[0], (self.x, self.y))


    class Knight:
        def __init__(self, x, y, xMin, xMax, yMin, yMax, pics, mask, hit):
            self.x = x
            self.y = y
            self.xMin = xMin
            self.distance=950
            self.xMax = xMax
            self.yMin = yMin
            self.yMax = yMax
            self.pics= pics
            self.mask = mask
            self.hit = hit
            self.counter=random.randint(0,8)
            self.counter2 = 10
            self.counter3 = 29
            self.dead=False
            self.walking=random.randint(0,1)

        def revive(self):
            self.distance=950
            self.x=self.counter=random.randint(200,size[0]-800)
            self.hit = False
            self.counter=random.randint(0,8)
            self.counter2 = 10
            self.counter3 = 29
            self.dead=False
            self.walking=random.randint(0,1)



        def draw(self):
            global points
            global wall_life
            if self.hit and not self.dead:
                #dying
                screen.blit(self.pics[self.counter2], (self.x, self.y))
                self.counter2+=1
                self.speed=0
                if self.counter2==18:
                    self.dead=True
                    points+=5


            elif not self.dead:
                #attacking
                if self.x >= self.distance:
                    screen.blit(self.pics[self.counter3], (self.x, self.y))
                    self.counter3 += 1

                    if self.counter3 == 38:
                        self.counter3 = 29
                        wall_life = wall_life - 1
                #walking
                elif self.walking:
                    self.speed=0.5
                    self.x += self.speed
                    screen.blit(self.pics[self.counter], (self.x, self.y))
                    self.counter += 1
                    if self.counter == 9:
                        self.counter=0
                #running
                else:
                    self.speed = 1
                    self.x += self.speed
                    screen.blit(self.pics[self.counter+19], (self.x, self.y))
                    self.counter += 1
                    if self.counter == 9:
                        self.counter=0
            #dead
            else:
                screen.blit(self.pics[18], (self.x, self.y))





    background = create_background(pygame.Surface((size)))
    wall_fence = create_wall(pygame.Surface((100,550)))



    def drawBackgroundAnimations(iAnimation):
        screen.blit(background,(0,0))
        if not game_lost:
            screen.blit(wall_fence, (1000, 200))
        screen.blit(pic_coin[iAnimation], (1200, 450))
        screen.blit(pic_campfire[iAnimation], (1260, 315))
        #screen.blit(pic_knight[iAnimation], (1260, 315))



    #define masks
    Diabolo = pygame.image.load(os.path.join(path,"pics/Schuss.png"))
    Diabolo_Mask = pygame.mask.from_surface(Diabolo)
    Diabolo_Rect = Diabolo.get_rect(center=(50,50))
    #include pictures


    wizard_mask = pygame.mask.from_surface(pic_Wizard[0])

    NullSchuss = pygame.Rect(0, 0, 15, 15)
    Schuss = pygame.Rect(0, 0, 15, 15)


    Wizard_list=[]
    Wizard_count=0
    for i in range(0,Wizard_count):
        Wizard_list.append(Wizard(random.randint(200,size[0]-400),random.randint(200,size[1]-200),2,5,1275,5,768, pic_Wizard, wizard_mask, False))


    GAME_FONT = pygame.font.SysFont("Times", 50)

    go = True
    hit_for_screenshot=False
    screenshot_delay=0

    knight_mask = pygame.mask.from_surface(pic_knight[0])
    Knight_list=[]
    Knight_count=50
    for i in range(0,Knight_count):
        Knight_list.append(Knight(random.randint(100,size[0]-800),random.randint(200,size[1]-200),5,1275,5,768, pic_knight,knight_mask, False))
    # Start Game

    while hmsysteme.game_isactive():
        #screen.fill(BLACK)
        #print(wall_life)


        #Nackground Animations
        drawBackgroundAnimations(iAnimation)

        iAnimation += 1
        if iAnimation > 9:
            iAnimation = 0

        for i in range(0, Wizard_count):
            Wizard_list[i].draw()

        count = 0
        for i in range(0, Knight_count):
            if Knight_list[i].dead== True:
                Knight_list[i].draw()
                count=count+Knight_list[i].dead
        for i in range(0, Knight_count):
            if Knight_list[i].dead == False:
                Knight_list[i].draw()


        if count==Knight_count:
            for i in range(0, Knight_count):
                Knight_list[i].revive()




        if wall_life<=0:
            game_lost=True
            text = GAME_FONT.render("DEFEAT", True, (255, 0, 0))
            for i in range(0, Knight_count):
                Knight_list[i].distance=1200
            #print("lost")
        else:
            text = GAME_FONT.render(str(wall_life), True, (255, 0, 0))
            #print("not lost")



        screen.blit(text, (1000, 150))
        text = GAME_FONT.render(str(points), True, (0, 255, 0))
        screen.blit(text, (200, 150))


        for event in pygame.event.get():
            # Beenden bei [ESC] oder [X]
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                hit_for_screenshot = True
                mausx = event.pos[0]  # pos = pygame.mouse.get_pos() MAUSPOSITION ingame
                mausy = event.pos[1]
                print("X:", mausx, "Y:", mausy)
                Schuss = pygame.Rect(mausx - 8, mausy - 8, 15, 15)
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 10, 10)

                for i in range(0,Knight_count):
                    offsetKnight=(mausx - int(Knight_list[i].x), int(mausy-Knight_list[i].y))
                    if Knight_list[i].mask.overlap(Diabolo_Mask, offsetKnight):
                        Knight_list[i].hit = True

                for i in range(0,Wizard_count):
                    offsetWizard=(mausx - Wizard_list[i].x, mausy-Wizard_list[i].y)
                    if Wizard_list[i].mask.overlap(Diabolo_Mask, offsetWizard):
                        Wizard_list[i].hit = True

        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            Schuss = pygame.Rect(pos[0] - 8, pos[1] - 8, 15, 15)
            Diabolo_Rect = pygame.Rect(pos[0] - 15, pos[1] - 15, 10, 10)

            for i in range(0, Knight_count):
                offsetKnight = (int(pos[0] - Knight_list[i].x), int(pos[1] - Knight_list[i].y))
                if Knight_list[i].mask.overlap(Diabolo_Mask, offsetKnight):
                    Knight_list[i].hit = True





        if hit_for_screenshot:
            screenshot_delay+=1
            if screenshot_delay==10:
                screen.blit(Diabolo, Diabolo_Rect)
                pygame.display.flip()
                #start=time.time()
                #hmsysteme.take_screenshot(screen)
                #print(time.time()-start)

                start=time.time()
                hmsysteme.take_screenshot(screen)
                print(time.time()-start)
                #print("screenshot")
                screenshot_delay=0
                hit_for_screenshot=False


        clock.tick(20)
        pygame.display.flip()
        #print(clock.get_fps())
    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()

