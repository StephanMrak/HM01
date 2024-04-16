
def main():
    global xBoatDamaged, xHitBoat, iCampfire, iCoin, checkCoin, timebar_width, iExplosion, xBoatDone, hit_for_screenshot, xHitAltar, xAltar_done, iAltar, xCow_done, iCow, xHitCow
    import pygame
    import time
    import hmsysteme
    import os
    import platform
    import pygame.freetype
    print(platform.uname())
    # some colors to use
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 191, 255)
    RED = (255, 0, 0)
    HIMMELBLAU = (120, 210, 255)
    YELLOW = (255, 255, 0)
    xbackground = 0
    ybackground = 0
    xCow_done = False
    iCow = 0
    xHitCow = False
    iBackgroundAnimation = 0
    framerate =30
    frames = 0
    offsetDiabolo = 9
    # Pygame init
    iCampfire = 0
    iCoin = 0
    iHarpye = 0
    pygame.init()
    iExplosion = 0
    xBoatDamaged = False
    xHitBoat = False
    xBoatDone = False
    # Variablen init
    mausx = 0
    mausy = 0
    offsetChest = 0
    ChestHit = False
    CoinHit = False
    ZombieHit = False
    HarpyieHit = False
    LockHit = False
    txtHit_x = 0
    txtHit_y = 560
    txt_counter = 0
    ChestGame = True
    Game_Over = False
    checkCoin = False
    checkZombie = False
    offsetLock = 0
    posChest = (290,535)
    z_direction = 0
    z_hit = 0
    Zombies = []
    Harpyienen = []
    offsetZombie = (0,0)
    timerZombie = 0
    timerHarpyie = 0
    timebar_width = 683
    xAltar_done = False
    xHitAltar = False
    iAltar = 0
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #size = [1366, 768]
    size = hmsysteme.get_size()
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    names = hmsysteme.get_playernames()
    if not names:
        names = ["Stephan", "Marion", "Flori", "Peter Mafai"]

    path = os.path.realpath(__file__)
#    path = path.replace('Prestige\Prestige.py', '')
    if 'Linux' in platform.uname():
        path = path.replace('Prestige.py', '')
    else:
        path = path.replace('Prestige.py', '')

    #path = r"C:/Users/flori/Dropbox/Telespiel/Raspi_Programme/HM01_v0.1/"

    #screen = pygame.display.set_mode(size)
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    print(path)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Prestige")

    #Bilder
    pic_background = pygame.image.load(os.path.join(path, "pics/Background/Competition/background.png"))
    pic_background_animation = [pygame.image.load(os.path.join(path,"pics/Background/Competition/cross2.png"))]  #0

    pic_campfire = [pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire1.png")),  #0
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire2.png")),  #2
                    pygame.image.load(os.path.join(path,"pics/Background/Competition/CampFire3.png")),  #4
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/CampFire4.png")), #6
                    pygame.image.load(os.path.join(path, "pics/Background/Competition/CampFire5.png"))] #9

    pic_coin = [pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold1.png")),  #0
                pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold2.png")),  #2
                pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold3.png")),  #3
                pygame.image.load(os.path.join(path,"pics/Background/Competition/coin_gold4.png")),  #4
                pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold5.png")), #5
                pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold6.png")), #6
                pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold7.png")), #7
                pygame.image.load(os.path.join(path, "pics/Background/Competition/coin_gold8.png")),]#9

    pic_Wizard = [pygame.image.load(os.path.join(path,"pics/Wizard/wizard1.png")), pygame.image.load(os.path.join(path,"pics/Wizard/wizard2.png")),
                 pygame.image.load(os.path.join(path,"pics/Wizard/wizard3.png")), pygame.image.load(os.path.join(path,"pics/Wizard/wizard4.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard5.png")), pygame.image.load(os.path.join(path,"pics/Wizard/wizard6.png")),
                  pygame.image.load(os.path.join(path,"pics/Wizard/wizard7.png")), pygame.image.load(os.path.join(path,"pics/Wizard/wizard8.png"))]

    pic_Harpye = [pygame.image.load(os.path.join(path,"pics/Harpye/harpye1.png")),pygame.image.load(os.path.join(path,"pics/Harpye/harpye2.png")),
                  pygame.image.load(os.path.join(path,"pics/Harpye/harpye3.png")),pygame.image.load(os.path.join(path,"pics/Harpye/harpye4.png")),
                  pygame.image.load(os.path.join(path,"pics/Harpye/harpye5.png")),pygame.image.load(os.path.join(path,"pics/Harpye/harpye6.png")),
                  pygame.image.load(os.path.join(path,"pics/Harpye/harpye7.png"))]

    pic_Harpye_dead = [pygame.image.load(os.path.join(path,"pics/Harpye/harpye_die1.png")),pygame.image.load(os.path.join(path,"pics/Harpye/harpye_die2.png")),
                  pygame.image.load(os.path.join(path,"pics/Harpye/harpye_die3.png")),pygame.image.load(os.path.join(path,"pics/Harpye/harpye_die4.png")),
                  pygame.image.load(os.path.join(path,"pics/Harpye/harpye_die5.png")),pygame.image.load(os.path.join(path,"pics/Harpye/harpye_die6.png")),
                  pygame.image.load(os.path.join(path,"pics/Harpye/harpye_die7.png"))]

    pic_zombie_ro = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro1.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro2.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro3.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro4.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro5.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro6.png"))]
    pic_zombie_lo = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo1.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo2.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo3.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo4.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo5.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo6.png"))]
    pic_zombie_lu = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu1.png")),pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu2.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu3.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu4.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu5.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu6.png"))]
    pic_zombie_ru = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru1.png")),pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru2.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru3.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru4.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru5.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru6.png"))]
    pic_zombie_lodown = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo11.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo12.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo13.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo14.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo15.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo16.png"))]
    pic_zombie_rodown = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro11.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro12.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro13.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro14.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro15.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro16.png"))]
    pic_zombie_ludown = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu11.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu12.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu13.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu14.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu15.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu16.png"))]
    pic_zombie_rudown = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru11.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru12.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru13.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru14.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru15.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru16.png"))]
    pic_zombie_dead_lo = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro21.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro22.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo23.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo24.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo25.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo26.png")),
                       pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo27.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lo28.png"))]
    pic_zombie_dead_ro = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro21.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro22.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro23.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro24.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro25.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro26.png")),
                       pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro27.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ro28.png"))]
    pic_zombie_dead_lu = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu21.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu22.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu23.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu24.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu25.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu26.png")),
                       pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu27.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_lu28.png"))]
    pic_zombie_dead_ru = [pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru21.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru22.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru23.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru24.png")),
                    pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru25.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru26.png")),
                       pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru27.png")), pygame.image.load(os.path.join(path,"pics/Zombie/zombie_ru28.png"))]

    pic_chest = [pygame.image.load(os.path.join(path,"pics/Background/Competition/chest0.png")),
                 pygame.image.load(os.path.join(path,"pics/Background/Competition/chest1.png"))]
    pic_timebar = [pygame.image.load(os.path.join(path,"pics/Background/Competition/timebar.png")),
                   pygame.image.load(os.path.join(path,"pics/Background/Competition/timebar1.png"))]
    pic_lock = [pygame.image.load(os.path.join(path,"pics/Background/Competition/lock1.png")),
                pygame.image.load(os.path.join(path,"pics/Background/Competition/lock2.png")),]

    pic_boat = [pygame.image.load(os.path.join(path,"pics/Background/Competition/boot.png")),
                pygame.image.load(os.path.join(path,"pics/Background/Competition/boot_damaged.png")),]

    pic_explosion = [pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/0.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/1.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/2.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/3.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/4.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/5.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/6.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/7.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/8.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/9.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/10.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/11.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/12.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/13.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/14.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/15.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/16.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/17.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/18.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Explosion/19.png")),]

    pic_barrel = pygame.image.load(os.path.join(path,"pics/Prestige/barrel.png"))
    pic_barrel_sc = pygame.transform.scale(pic_barrel, (50, 50))

    pic_altar =     [pygame.image.load(os.path.join(path,"pics/Prestige/Altar/0.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/1.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/2.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/3.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/4.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/5.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/6.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/7.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/8.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/9.png")),]

    pic_altar_ex =  [pygame.image.load(os.path.join(path,"pics/Prestige/Altar/11.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/12.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/13.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/14.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/15.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/16.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/17.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/18.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/19.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Altar/20.png"))]

    pic_cow =       [pygame.image.load(os.path.join(path,"pics/Prestige/Cow/1.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/2.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/3.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/4.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/5.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/6.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/7.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/8.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/9.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/10.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/11.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/12.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/13.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/14.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/15.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/16.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/17.png")),
                     pygame.image.load(os.path.join(path,"pics/Prestige/Cow/18.png"))]

    class Player:
        def __init__(self, name, score):
            self.name = name
            self.score = score

    class Zombie:
        def __init__(self, x, y, mask, hit1, hit2):
            global offsetZombie
            self.x = x
            self.y = y
            self.mask = mask
            self.hit1 = hit1
            self.hit2 = hit2
            self.speed = 1
            self.direction = 0
            self.picture = 0
            self.picture6 = 0
            self.picture6rev = 35
            self.picture8 = 0
            self.xcounter = 0
            self.counter_pics = 0
            self.hit_done = False
            self.down = False
            self.up = False
            self.dead = False
            self.stop = False
            self.counter_hit = 0
            self.counter_down = 0
            self.counter_up = 35
            self.counter_dead = 0
            self.picturetest = 0

        def draw(self):
            global ZombieHit

            #rechts oben
            if self.direction == 0:
                if not self.stop:
                    screen.blit(pic_zombie_ro[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                    self.x += self.speed
                    self.y -= self.speed / 2
                    self.xcounter += 1
                    if self.xcounter > 210:
                        self.direction = 1
                        self.xcounter = 0

                if self.hit1 and not self.hit_done:
                    self.picture = 0
                    screen.blit(pic_zombie_rodown[self.picture6 // 6], (self.x, self.y))
                    if self.picture6 == 35:
                        self.picture6 = 0
                        self.hit_done = True
                    self.picture6 += 1
                    self.stop = True

                if self.hit_done and not self.down:
                    screen.blit(pic_zombie_rodown[5], (self.x, self.y))
                    self.counter_down += 1
                    self.stop = True
                    if self.counter_down > 120:
                        self.down = True
                if self.down and not self.up:
                    screen.blit(pic_zombie_rodown[self.picture6rev // 6], (self.x, self.y))
                    self.picture6rev -= 1
                    if self.picture6rev == 0:
                        self.up = True
                        self.stop = False
                if self.up and not self.hit2:
                    screen.blit(pic_zombie_ro[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                if self.hit2:
                    self.stop = True
                    ZombieHit = True

                    if self.picture8 < 64:
                        screen.blit(pic_zombie_dead_ro[self.picture8 // 8], (self.x, self.y))
                    else:
                        screen.blit(pic_zombie_dead_ro[7], (self.x, self.y))
                    self.picture8 += 1
                    if self.picture8 == 62:
                        self.dead = True

            #links oben
            if self.direction == 1:
                if not self.stop:
                    screen.blit(pic_zombie_lo[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                    self.x -= self.speed
                    self.y -= self.speed / 2
                    self.xcounter += 1
                    if self.xcounter > 190:
                        self.direction = 2
                        self.xcounter = 0

                if self.hit1 and not self.hit_done:
                    self.picture = 0
                    screen.blit(pic_zombie_lodown[self.picture6 // 6], (self.x, self.y))
                    if self.picture6 == 35:
                        self.picture6 = 0
                        self.hit_done = True
                    self.picture6 += 1
                    self.stop = True

                if self.hit_done and not self.down:
                    screen.blit(pic_zombie_lodown[5], (self.x, self.y))
                    self.counter_down += 1
                    self.stop = True
                    if self.counter_down > 120:
                        self.down = True
                if self.down and not self.up:
                    screen.blit(pic_zombie_lodown[self.picture6rev // 6], (self.x, self.y))
                    self.picture6rev -= 1
                    if self.picture6rev == 0:
                        self.up = True
                        self.stop = False
                if self.up and not self.hit2:
                    screen.blit(pic_zombie_lo[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                if self.hit2:
                    self.stop = True
                    ZombieHit = True

                    if self.picture8 < 64:
                        screen.blit(pic_zombie_dead_lo[self.picture8 // 8], (self.x, self.y))
                    else:
                        screen.blit(pic_zombie_dead_lo[7], (self.x, self.y))
                    self.picture8 += 1
                    if self.picture8 == 62:
                        self.dead = True

            #rechts unten
            if self.direction == 2:
                if not self.stop:
                    screen.blit(pic_zombie_ru[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                    self.x += self.speed
                    self.y += self.speed / 2
                    self.xcounter += 1
                    if self.xcounter > 190:
                        self.direction = 3
                        self.xcounter = 0

                if self.hit1 and not self.hit_done:
                    self.picture = 0
                    screen.blit(pic_zombie_rudown[self.picture6 // 6], (self.x, self.y))
                    if self.picture6 == 35:
                        self.picture6 = 0
                        self.hit_done = True
                    self.picture6 += 1
                    self.stop = True

                if self.hit_done and not self.down:
                    screen.blit(pic_zombie_rudown[5], (self.x, self.y))
                    self.counter_down += 1
                    self.stop = True
                    if self.counter_down > 120:
                        self.down = True
                if self.down and not self.up:
                    screen.blit(pic_zombie_rudown[self.picture6rev // 6], (self.x, self.y))
                    self.picture6rev -= 1
                    if self.picture6rev == 0:
                        self.up = True
                        self.stop = False
                if self.up and not self.hit2:
                    screen.blit(pic_zombie_ru[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                if self.hit2:
                    self.stop = True
                    ZombieHit = True

                    if self.picture8 < 64:
                        screen.blit(pic_zombie_dead_ru[self.picture8 // 8], (self.x, self.y))
                    else:
                        screen.blit(pic_zombie_dead_ru[7], (self.x, self.y))
                    self.picture8 += 1
                    if self.picture8 == 62:
                        self.dead = True

            #links unten
            if self.direction == 3:
                if not self.stop:
                    screen.blit(pic_zombie_lu[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                    self.x -= self.speed
                    self.y += self.speed / 2
                    self.xcounter += 1
                    if self.xcounter > 210:
                        self.direction = 0
                        self.xcounter = 0

                if self.hit1 and not self.hit_done:
                    self.picture = 0
                    screen.blit(pic_zombie_ludown[self.picture6 // 6], (self.x, self.y))
                    if self.picture6 == 35:
                        self.picture6 = 0
                        self.hit_done = True
                    self.picture6 += 1
                    self.stop = True

                if self.hit_done and not self.down:
                    screen.blit(pic_zombie_ludown[5], (self.x, self.y))
                    self.counter_down += 1
                    self.stop = True
                    if self.counter_down > 120:
                        self.down = True
                if self.down and not self.up:
                    screen.blit(pic_zombie_ludown[self.picture6rev // 6], (self.x, self.y))
                    self.picture6rev -= 1
                    if self.picture6rev == 0:
                        self.up = True
                        self.stop = False
                if self.up and not self.hit2:
                    screen.blit(pic_zombie_lu[self.picture // 6], (self.x, self.y))
                    if self.picture == 35:
                        self.picture = 0
                    self.picture += 1
                if self.hit2:
                    self.stop = True
                    ZombieHit = True

                    if self.picture8 < 64:
                        screen.blit(pic_zombie_dead_lu[self.picture8 // 8], (self.x, self.y))
                    else:
                        screen.blit(pic_zombie_dead_lu[7], (self.x, self.y))
                    self.picture8 += 1
                    if self.picture8 == 62:
                        self.dead = True

            #Kreuz neu zeichnen
            screen.blit(pic_background_animation[0], (126, 532))

    class Harpyie:
        def __init__(self, x, y, mask, hit):
            global offsetHarpyie
            self.x = x
            self.y = y
            self.mask = mask
            self.hit = hit
            self.stop = False
            self.picture = 0
            self.picturex = 0
            self.speed = 3
            self.direction = 0
            self.dead = False
            self.done = False

        def draw(self):
            global HarpyieHit

            if self.hit:
                self.stop = True
                screen.blit(pic_Harpye_dead[self.picturex // 7], (self.x, self.y))
                if self.picturex < 48:
                    self.picturex += 1
                    self.dead = True
                else:
                    self.done = True

            if not self.stop:
                if self.direction == 0:
                        screen.blit(pic_Harpye[self.picture // 7], (self.x, self.y))
                        if self.picture == 48:
                            self.picture = 0
                        self.picture += 1
                        self.x += self.speed
                        self.y += self.speed / 1.5
                        if self.x > 200:
                            self.direction = 1

                if self.direction == 1:
                        screen.blit(pic_Harpye[self.picture // 7], (self.x, self.y))
                        if self.picture == 48:
                            self.picture = 0
                        self.picture += 1
                        self.x += self.speed * 1.5
                        if self.x > 1000:
                            self.direction = 2

                if self.direction == 2:
                        screen.blit(pic_Harpye[self.picture // 7], (self.x, self.y))
                        if self.picture == 48:
                            self.picture = 0
                        self.picture += 1
                        self.x += self.speed
                        self.y -= self.speed / 1.5
                        if self.x > 1400:
                            self.direction = 0
                            self.x = -50
                            self.y = 150

            if self.done:
                screen.blit(pic_Harpye_dead[6], (self.x, self.y))

    #Timebar
    def update_timebar(CoinHit,ZombieHit):
        global timebar_width
        global checkCoin, checkZombie
        if CoinHit and not checkCoin:
            timebar_width = timebar_width + 60
            checkCoin = True
        if ZombieHit and not checkZombie:
            timebar_width = timebar_width + 60
            checkZombie = True

    def zeichnen(x, y, iBackgroundAnimation, ChestHit, CoinHit, LockHit, txtHit_y, Game_Over):
        global iCampfire, iCoin, iHarpye, iExplosion, xHitBoat, xBoatDamaged, xBoatDone, iAltar, xAltar_done, xHitCow, xCow_done, iCow
        #screen.fill(BLACK)
        screen.blit(pic_background, (0, 0))

        #Minigame Chest
        if not CoinHit and not ChestHit and not LockHit:
            screen.blit(pic_chest[0], posChest)
            screen.blit(pic_lock[0], (303, 596))
        if not CoinHit and not ChestHit and LockHit:
            screen.blit(pic_chest[0], posChest)
            screen.blit(pic_lock[1], (303, 596))
        if ChestHit and LockHit and not CoinHit:
            screen.blit(pic_chest[1], posChest)
            screen.blit(pic_coin[iCoin//2], (310, 573))
            iCoin += 1
            if iCoin == 15:
                iCoin = 0
            screen.blit(pic_lock[1], (303, 596))
        if CoinHit:
            screen.blit(pic_chest[1], posChest)
            screen.blit(pic_lock[1], (303, 596))
            if txtHit_y > 450:
                screen.blit(txtHit, (295, txtHit_y))
        #Boat
        if xBoatDamaged:
            screen.blit(pic_boat[1], (750, 500))
        else:
            screen.blit(pic_boat[0], (750, 500))
            screen.blit(pic_barrel_sc, (808, 532))
        if xHitBoat:
            #screen.blit(pic_boat[0], (750, 500))
            screen.blit(pic_explosion[iExplosion//3], (750, 490))
            iExplosion += 1
            if iExplosion == 30:
                xBoatDamaged = True
            if iExplosion >= 60:
                xHitBoat = False
                xBoatDone = True

        #Altar
        if not xHitAltar:
            screen.blit(pic_altar[0], (1000, 450))
        if xHitAltar and not xAltar_done:
            screen.blit(pic_altar[iAltar // 5], (1000, 450))
            screen.blit(pic_altar_ex[iAltar // 5], (1030, 400))
            iAltar += 1
            if iAltar > 49:
                xAltar_done = True
        if xAltar_done:
            screen.blit(pic_altar[9], (1000, 450))

        if not xHitCow:
            screen.blit(pic_cow[0], (600, 105))
        if xHitCow and not xCow_done:
            screen.blit(pic_cow[iCow // 9], (600, 105))
            iCow += 1
            if iCow > 80:
                xCow_done = True
        if xCow_done:
            screen.blit(pic_cow[17], (600, 105))

        #Backgroundanimations
        #Campfire
        screen.blit(pic_campfire[iCampfire // 5], (154, 221))
        iCampfire += 1
        if iCampfire == 24:
            iCampfire = 0

        #Zombies
        for i in range(0, len(Zombies)):
            Zombies[i].draw()

        #Harpyienen
        for i in range(0, len(Harpyienen)):
            Harpyienen[i].draw()

        #Timebar
        pic_timebar[1] = pygame.transform.scale(pic_timebar[1], (timebar_width, 50))
        timebar1_rect = pic_timebar[1].get_rect(midleft=(1025 - timebar_width,700))
        screen.blit(pic_timebar[0], timebar_rect)
        screen.blit(pic_timebar[1], timebar1_rect)
        if Game_Over:
            txt_score = GAME_FONT.render("Score: " + str(frames), True, (255, 255, 255))
            screen.blit(txt_score, (600, 300))

        screen.blit(Diabolo, Diabolo_Rect)
        pygame.display.flip()

    # Init Game
    #define masks
    Diabolo = pygame.image.load(os.path.join(path,"pics/Schuss.png"))
    MaskDiabolo = pygame.mask.from_surface(Diabolo)
    Diabolo_Rect = Diabolo.get_rect(center=(50,50))
    timebar_rect = pic_timebar[0].get_rect(center=(687,700))
    mask_chest = pygame.mask.from_surface(pic_chest[0])
    mask_Coin = pygame.mask.from_surface(pic_coin[0])
    mask_lock = pygame.mask.from_surface(pic_lock[0])
    mask_Altar = pygame.mask.from_surface(pic_altar[0])

    NullSchuss = pygame.Rect(0, 0, 15, 15)
    Schuss = pygame.Rect(0, 0, 15, 15)

    GAME_FONT = pygame.font.SysFont("Times", 25)
    text = GAME_FONT.render("Hello, World", True, (0, 128, 0))
    hit_for_screenshot = False
    screenshot_delay = 0

    mask_zombie = pygame.mask.from_surface(pic_zombie_lodown[0])
    Zombies.append(Zombie(-10, 620, mask_zombie, False, False))
    mask_hapyie = pygame.mask.from_surface(pic_Harpye[0])
    Harpyienen.append(Harpyie(-50,150,mask_hapyie,False))
    mask_barell = pygame.mask.from_surface(pic_barrel_sc)
    mask_cow = pygame.mask.from_surface(pic_cow[0])
    # Start Game
    while hmsysteme.game_isactive():
        for event in pygame.event.get():
            # Beenden bei [ESC] oder [X]
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                hit_for_screenshot = True
                print(hit_for_screenshot)
                mausx = event.pos[0]  # pos = pygame.mouse.get_pos() MAUSPOSITION ingame
                mausy = event.pos[1]
                print("X:", mausx, "Y:", mausy)
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
                screen.blit(Diabolo, Diabolo_Rect)

                # Screenshot
                if hit_for_screenshot:
                    screen.blit(Diabolo, Diabolo_Rect)
                    pygame.display.flip()
                    hmsysteme.take_screenshot(screen)
                    hit_for_screenshot = False

                #actualize Masks
                #Minigame Chest
                offsetChest = ((mausx - (290+offsetDiabolo)), int(mausy - (535+offsetDiabolo)))
                offsetCoin = ((mausx - (310+offsetDiabolo)), int(mausy - (570+offsetDiabolo)))
                offsetLock = ((mausx - (303+offsetDiabolo)), int(mausy - (596+offsetDiabolo)))
                if mask_Coin.overlap(MaskDiabolo, offsetCoin) and ChestHit and LockHit:
                    CoinHit = True
                    txtHit = GAME_FONT.render("+10", True, (0, 255, 0))
                if mask_chest.overlap(MaskDiabolo, offsetChest) and LockHit:
                    ChestHit = True
                if mask_lock.overlap(MaskDiabolo, offsetLock):
                    LockHit = True

                # Zombies
                for i in range(0, len(Zombies)):
                    offsetZombie = (mausx - (int(Zombies[i].x + offsetDiabolo)), mausy - (int(Zombies[i].y + offsetDiabolo)))
                    if Zombies[i].mask.overlap(MaskDiabolo, offsetZombie):
                        Zombies[i].hit1 = True
                    if Zombies[i].mask.overlap(MaskDiabolo, offsetZombie) and Zombies[i].up:
                        Zombies[i].hit2 = True

                # Harpyien
                for i in range(0, len(Harpyienen)):
                    offsetHarpyie = (
                    mausx - (int(Harpyienen[i].x + offsetDiabolo)), mausy - (int(Harpyienen[i].y + offsetDiabolo)))
                    if Harpyienen[i].mask.overlap(MaskDiabolo, offsetHarpyie):
                        Harpyienen[i].hit = True

                #Boat
                if not xBoatDone:
                    offsetBarrel = ((mausx - (808 + offsetDiabolo)), int(mausy - (532 + offsetDiabolo)))
                    if mask_barell.overlap(MaskDiabolo, offsetBarrel):
                        xHitBoat = True

                #Altar
                if not xAltar_done:
                    offsetAltar = ((mausx - (1000 + offsetDiabolo)), int(mausy - (450 + offsetDiabolo)))
                    if mask_Altar.overlap(MaskDiabolo, offsetAltar):
                        xHitAltar = True

                #Cow
                if not xCow_done:
                    offsetCow = ((mausx - (600 + offsetDiabolo)), int(mausy - (105 + offsetDiabolo)))
                    if mask_cow.overlap(MaskDiabolo, offsetCow):
                        xHitCow = True

        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            mausx = pos[0]
            mausy = pos[1]
            Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
            screen.blit(Diabolo, Diabolo_Rect)

            # Screenshot
            if hit_for_screenshot:
                screen.blit(Diabolo, Diabolo_Rect)
                pygame.display.flip()
                hmsysteme.take_screenshot(screen)
                hit_for_screenshot = False

            # actualize Masks
            # Minigame Chest
            offsetChest = ((mausx - (290 + offsetDiabolo)), int(mausy - (535 + offsetDiabolo)))
            offsetCoin = ((mausx - (310 + offsetDiabolo)), int(mausy - (570 + offsetDiabolo)))
            offsetLock = ((mausx - (303 + offsetDiabolo)), int(mausy - (596 + offsetDiabolo)))
            if mask_Coin.overlap(MaskDiabolo, offsetCoin) and ChestHit and LockHit:
                CoinHit = True
                txtHit = GAME_FONT.render("+10", True, (0, 255, 0))
            if mask_chest.overlap(MaskDiabolo, offsetChest) and LockHit:
                ChestHit = True
            if mask_lock.overlap(MaskDiabolo, offsetLock):
                LockHit = True

            # Zombies
            for i in range(0, len(Zombies)):
                offsetZombie = (
                mausx - (int(Zombies[i].x + offsetDiabolo)), mausy - (int(Zombies[i].y + offsetDiabolo)))
                if Zombies[i].mask.overlap(MaskDiabolo, offsetZombie):
                    Zombies[i].hit1 = True
                if Zombies[i].mask.overlap(MaskDiabolo, offsetZombie) and Zombies[i].up:
                    Zombies[i].hit2 = True

            # Harpyien
            for i in range(0, len(Harpyienen)):
                offsetHarpyie = (
                    mausx - (int(Harpyienen[i].x + offsetDiabolo)), mausy - (int(Harpyienen[i].y + offsetDiabolo)))
                if Harpyienen[i].mask.overlap(MaskDiabolo, offsetHarpyie):
                    Harpyienen[i].hit = True

            # Boat
            if not xBoatDone:
                offsetBarrel = ((mausx - (808 + offsetDiabolo)), int(mausy - (532 + offsetDiabolo)))
                if mask_barell.overlap(MaskDiabolo, offsetBarrel):
                    xHitBoat = True

            # Altar
            if not xAltar_done:
                offsetAltar = ((mausx - (1000 + offsetDiabolo)), int(mausy - (450 + offsetDiabolo)))
                if mask_Altar.overlap(MaskDiabolo, offsetAltar):
                    xHitAltar = True

            # Cow
            if not xCow_done:
                offsetCow = ((mausx - (600 + offsetDiabolo)), int(mausy - (105 + offsetDiabolo)))
                if mask_cow.overlap(MaskDiabolo, offsetCow):
                    xHitCow = True

        #ChestGame
        if ChestGame:
            if CoinHit:
                txtHit_y -= 5
                if txtHit_y < 450:
                    ChestGame = False
        #Zombies
        for i in range(0, len(Zombies)):
            #print(len(Zombies))
            if Zombies[i].dead:
                timerZombie += 1
                if timerZombie > 120:
                    Zombies[i].dead = False
                    timerZombie = 0
                    Zombies.append(Zombie(-10, 620, mask_zombie, False, False))
        #Harpyie
        for i in range(0, len(Harpyienen)):
            if Harpyienen[i].dead:
                timerHarpyie += 1
                if timerHarpyie > 120:
                    Harpyienen[i].dead = False
                    Harpyienen[i].hit = False
                    timerHarpyie = 0
                    Harpyienen.append(Harpyie(-50, 150, mask_hapyie, False))

        #Backgroundanimations
        if iBackgroundAnimation > 9:
            iBackgroundAnimation = 0

        #Timebar
        if timebar_width > 5:
            timebar_width -= 1
        else:
            Game_Over = True
        update_timebar(CoinHit,ZombieHit)

        #Zeichnen
        zeichnen(mausx, mausy, iBackgroundAnimation, ChestHit, CoinHit, LockHit, txtHit_y, Game_Over)
        iBackgroundAnimation += 1

        if not Game_Over:
            frames += 1

        #Reset Diabolo (Remove for HMSysteme!!!!!)
        Diabolo_Rect = [-20, -20]
        Schuss = [0,0]
        mausx = 0
        mausy = 0

        clock.tick(framerate)
        #print(clock.get_fps())

if __name__ == '__main__':
    main()


