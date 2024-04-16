
def main():
    global mausx, mausy, xHit, iPoints, xReset, iCountShots, Biathlon_tmpScore, xBiathlon, iRound, iButtonStatus, xButtonEnter
    global xPistol10m, xRifle10m, xRifle15m, xBiathlon, xIntro, xButtonBack, xSettings, iButtonCount, xBlink
    global xRoundsSet, xShotsSet, iGlobalRounds, itmpGlobalRounds, xGameOver, iRoundShotsave, xSetRoundShots, iVerticalName
    global iHorizontalName, iHorizontalLine, iVerticalPoints, iHorizontalPoints, iLinePoints, xGameReset, iRoundCount, xInitial
    global xScoreBoard, xButtonPressed
    import pygame
    import hmsysteme
    import os
    import platform
    import pygame.freetype
    hmsysteme.put_button_names(["RESET", "+", "SCORE BOARD", "<", "Enter", ">", "BACK", "-", "BLIND SHOT"])
    print(platform.uname())
    # some colors to use
    FIREARMS = (70, 70, 70)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    #Variables
    framerate = 30
    pygame.init()
    Players = []
    offsetDiabolo = 9
    xHit = False
    iPoints = 0
    xReset = False
    xIntro = True
    xPistol10m = False
    xRifle10m = False
    xRifle15m = False
    xBiathlon = False
    Biathlon_tmpScore = [False, False, False, False, False]
    mausx = 0
    mausy = 0
    iRound = 0
    iVerticalName = 0
    iButtonStatus = 0
    xButtonEnter = False
    xButtonBack = False
    xSettings = False
    iButtonCount = 0
    xBlink = False
    xRoundsSet = False
    xShotsSet = False
    itmpGlobalRounds = 0
    xGameOver = False
    xSetRoundShots = False
    iHorizontalName = 100
    iHorizontalLine = 95
    iVerticalPoints = 0
    iHorizontalPoints = 0
    iLinePoints = 100
    xGameReset = False
    iRoundCount = []
    xInitial = True
    xScoreBoard = False
    xButtonPressed = False
    #####################!!!!!!!!!!!!!!!!###############
    #####Anfangschusszahl / Runden festlegen ###########
    iCountShots = 2
    iGlobalRounds = 2
    #####################!!!!!!!!!!!!!!!!###############
    iRoundShotsave = iCountShots

    #size = [1366, 768]
    size = hmsysteme.get_size()

    names = hmsysteme.get_playernames()
    if not names:
        names = ["Stephan", "Marion", "Flori", "Peter Mafai"]

    path = os.path.realpath(__file__)
    print(path)

    if 'Linux' in platform.uname():
        path = path.replace('Scheiben.py', '')
    else:
        path = path.replace('Scheiben.py', '')

    #screen = pygame.display.set_mode(size)
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    clock = pygame.time.Clock()
    pygame.display.set_caption("Scheiben")

    #Pics
    #Rifle 10m
    pic_rifle_score = pygame.transform.scale(pygame.image.load(os.path.join(path,"pics/Scheibe/gewehrw.png")),(40, 10))
    pic_Scheibe_rifle10m = [pygame.image.load(os.path.join(path, "pics/Scheibe/Rifle_10m/Kreis1.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis2.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis3.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis4.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis5.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis6.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis7.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis8.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis9.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Kreis10.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_10m/Reckteck.png"))]
    pic_Rifle = pygame.image.load(os.path.join(path,"pics/Scheibe/gewehr10m.png"))
    pic_Rifle_scale = pygame.transform.scale(pic_Rifle, (170,56))
    pic_pickrifle10m = pygame.image.load(os.path.join(path,"pics/Scheibe/gewehr10mw.png"))
    pic_pickrifle10m_sc = pygame.transform.scale(pic_pickrifle10m, (200,65))

    #Rifle 15m
    pic_Scheibe_rifle15m = [pygame.image.load(os.path.join(path, "pics/Scheibe/Rifle_15m/Kreis1.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis2.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis3.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis4.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis5.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis6.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis7.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis8.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis9.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Kreis10.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Rifle_15m/Rechteck.png"))]
    pic_Rifle15m = pygame.image.load(os.path.join(path,"pics/Scheibe/gewehr15m.png"))
    pic_Rifle15m_scale = pygame.transform.scale(pic_Rifle15m, (170,56))
    pic_pickrifle15m = pygame.image.load(os.path.join(path,"pics/Scheibe/gewehr15mw.png"))
    pic_pickrifle15m_sc = pygame.transform.scale(pic_pickrifle15m, (200,65))

    #Pistol 10m
    pic_Scheibe_pistol10m = [pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis1.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis2.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis3.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis4.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis5.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis6.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis7.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis8.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis9.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Kreis10.png")),
                   pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/Rechteck.png"))]
    pic_Pistol = pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/pistol.png"))
    pic_Pistol_scale = pygame.transform.scale(pic_Pistol, (100,95))
    pic_pickpistol10m = pygame.image.load(os.path.join(path,"pics/Scheibe/pistolw.png"))
    pic_pickpistol10m_sc = pygame.transform.scale(pic_pickpistol10m, (100,85))
    pic_PistolScore = pygame.transform.scale(pygame.image.load(os.path.join(path,"pics/Scheibe/Pistol_10m/pistolwxxx.png")),(35, 27))
    pic_buttonsettings = pygame.image.load(os.path.join(path,"pics/Scheibe/Settings.png"))
    pic_buttonsettings_sc = pygame.transform.scale(pic_buttonsettings, (100,52))

    #Biathlon
    pic_Biathlon = pygame.image.load(os.path.join(path,"pics/Scheibe/Biathlon/Biathlon.png"))
    pic_Biathlon_sc = pygame.transform.scale(pic_Biathlon, (100,146))
    #!!!!!!!!!Scheiben Schwer!!!!!!########
    pic_Biathlon_scheiben = [pygame.image.load(os.path.join(path,"pics/Scheibe/Biathlon/Schwer/1.png")),
                    pygame.image.load(os.path.join(path,"pics/Scheibe/Biathlon/Schwer/2.png")),
                    pygame.image.load(os.path.join(path,"pics/Scheibe/Biathlon/Schwer/3.png")),
                    pygame.image.load(os.path.join(path,"pics/Scheibe/Biathlon/Schwer/4.png")),
                    pygame.image.load(os.path.join(path,"pics/Scheibe/Biathlon/Schwer/5.png"))]
    pic_Biathlon_target = [pygame.image.load(os.path.join(path, "pics/Scheibe/Biathlon/Schwer/11.png")),
                    pygame.image.load(os.path.join(path, "pics/Scheibe/Biathlon/Schwer/21.png")),
                    pygame.image.load(os.path.join(path, "pics/Scheibe/Biathlon/Schwer/31.png")),
                    pygame.image.load(os.path.join(path, "pics/Scheibe/Biathlon/Schwer/41.png")),
                    pygame.image.load(os.path.join(path, "pics/Scheibe/Biathlon/Schwer/51.png"))]
    pic_Biathlon_Rechteck = pygame.image.load(os.path.join(path,"pics/Scheibe/Biathlon/Schwer/Rechteck.png"))
    pic_BiathlonScore = pygame.transform.scale(pygame.image.load(os.path.join(path, "pics/Scheibe/Biathlon/Biathlonw.png")), (32, 35))

#Create Masks
    #pistol 10m
    Mask_Pistol10m_1 = pygame.mask.from_surface(pic_Scheibe_pistol10m[0])
    Mask_Pistol10m_2 = pygame.mask.from_surface(pic_Scheibe_pistol10m[1])
    Mask_Pistol10m_3 = pygame.mask.from_surface(pic_Scheibe_pistol10m[2])
    Mask_Pistol10m_4 = pygame.mask.from_surface(pic_Scheibe_pistol10m[3])
    Mask_Pistol10m_5 = pygame.mask.from_surface(pic_Scheibe_pistol10m[4])
    Mask_Pistol10m_6 = pygame.mask.from_surface(pic_Scheibe_pistol10m[5])
    Mask_Pistol10m_7 = pygame.mask.from_surface(pic_Scheibe_pistol10m[6])
    Mask_Pistol10m_8 = pygame.mask.from_surface(pic_Scheibe_pistol10m[7])
    Mask_Pistol10m_9 = pygame.mask.from_surface(pic_Scheibe_pistol10m[8])
    Mask_Pistol10m_10 = pygame.mask.from_surface(pic_Scheibe_pistol10m[9])
    Mask_Pistol10m_0 = pygame.mask.from_surface(pic_Scheibe_pistol10m[10])
    #rifle 10m
    Mask_rifle10m_1 = pygame.mask.from_surface(pic_Scheibe_rifle10m[0])
    Mask_rifle10m_2 = pygame.mask.from_surface(pic_Scheibe_rifle10m[1])
    Mask_rifle10m_3 = pygame.mask.from_surface(pic_Scheibe_rifle10m[2])
    Mask_rifle10m_4 = pygame.mask.from_surface(pic_Scheibe_rifle10m[3])
    Mask_rifle10m_5 = pygame.mask.from_surface(pic_Scheibe_rifle10m[4])
    Mask_rifle10m_6 = pygame.mask.from_surface(pic_Scheibe_rifle10m[5])
    Mask_rifle10m_7 = pygame.mask.from_surface(pic_Scheibe_rifle10m[6])
    Mask_rifle10m_8 = pygame.mask.from_surface(pic_Scheibe_rifle10m[7])
    Mask_rifle10m_9 = pygame.mask.from_surface(pic_Scheibe_rifle10m[8])
    Mask_rifle10m_10 = pygame.mask.from_surface(pic_Scheibe_rifle10m[9])
    Mask_rifle10m_0 = pygame.mask.from_surface(pic_Scheibe_rifle10m[10])
    #rifle 15m
    Mask_rifle15m_1 = pygame.mask.from_surface(pic_Scheibe_rifle15m[0])
    Mask_rifle15m_2 = pygame.mask.from_surface(pic_Scheibe_rifle15m[1])
    Mask_rifle15m_3 = pygame.mask.from_surface(pic_Scheibe_rifle15m[2])
    Mask_rifle15m_4 = pygame.mask.from_surface(pic_Scheibe_rifle15m[3])
    Mask_rifle15m_5 = pygame.mask.from_surface(pic_Scheibe_rifle15m[4])
    Mask_rifle15m_6 = pygame.mask.from_surface(pic_Scheibe_rifle15m[5])
    Mask_rifle15m_7 = pygame.mask.from_surface(pic_Scheibe_rifle15m[6])
    Mask_rifle15m_8 = pygame.mask.from_surface(pic_Scheibe_rifle15m[7])
    Mask_rifle15m_9 = pygame.mask.from_surface(pic_Scheibe_rifle15m[8])
    Mask_rifle15m_10 = pygame.mask.from_surface(pic_Scheibe_rifle15m[9])
    Mask_rifle15m_0 = pygame.mask.from_surface(pic_Scheibe_rifle15m[10])
    #Biathlon
    Mask_Bia_1 = pygame.mask.from_surface(pic_Biathlon_scheiben[0])
    Mask_Bia_2 = pygame.mask.from_surface(pic_Biathlon_scheiben[1])
    Mask_Bia_3 = pygame.mask.from_surface(pic_Biathlon_scheiben[2])
    Mask_Bia_4 = pygame.mask.from_surface(pic_Biathlon_scheiben[3])
    Mask_Bia_5 = pygame.mask.from_surface(pic_Biathlon_scheiben[4])

    # Variablen init
    Players = []

    class Player:
        def __init__(self, name):
            self.name = name
            self.score_10mPistol = []
            self.score_10mRifle = []
            self.score_15mRifle = []
            self.score_Biathlon = []

    def Evaluation():
        global iPoints, xHit, Biathlon_tmpScore, xBiathlon, mausx, mausy
        xHit = True
        #Create Mask
        offset_Mask = ((mausx - offsetDiabolo), int(mausy - offsetDiabolo))
        # target evaluation pistol 10m
        if xPistol10m:
            if Mask_Pistol10m_10.overlap(MaskDiabolo, offset_Mask):
                iPoints = 10
            elif Mask_Pistol10m_9.overlap(MaskDiabolo, offset_Mask):
                iPoints = 9
            elif Mask_Pistol10m_8.overlap(MaskDiabolo, offset_Mask):
                iPoints = 8
            elif Mask_Pistol10m_7.overlap(MaskDiabolo, offset_Mask):
                iPoints = 7
            elif Mask_Pistol10m_6.overlap(MaskDiabolo, offset_Mask):
                iPoints = 6
            elif Mask_Pistol10m_5.overlap(MaskDiabolo, offset_Mask):
                iPoints = 5
            elif Mask_Pistol10m_4.overlap(MaskDiabolo, offset_Mask):
                iPoints = 4
            elif Mask_Pistol10m_3.overlap(MaskDiabolo, offset_Mask):
                iPoints = 3
            elif Mask_Pistol10m_2.overlap(MaskDiabolo, offset_Mask):
                iPoints = 2
            elif Mask_Pistol10m_1.overlap(MaskDiabolo, offset_Mask):
                iPoints = 1
            elif Mask_Pistol10m_0.overlap(MaskDiabolo, offset_Mask):
                iPoints = 0
        # target evaluation rifle 10m
        if xRifle10m:
            if Mask_rifle10m_10.overlap(MaskDiabolo, offset_Mask):
                iPoints = 10
            elif Mask_rifle10m_9.overlap(MaskDiabolo, offset_Mask):
                iPoints = 9
            elif Mask_rifle10m_8.overlap(MaskDiabolo, offset_Mask):
                iPoints = 8
            elif Mask_rifle10m_7.overlap(MaskDiabolo, offset_Mask):
                iPoints = 7
            elif Mask_rifle10m_6.overlap(MaskDiabolo, offset_Mask):
                iPoints = 6
            elif Mask_rifle10m_5.overlap(MaskDiabolo, offset_Mask):
                iPoints = 5
            elif Mask_rifle10m_4.overlap(MaskDiabolo, offset_Mask):
                iPoints = 4
            elif Mask_rifle10m_3.overlap(MaskDiabolo, offset_Mask):
                iPoints = 3
            elif Mask_rifle10m_2.overlap(MaskDiabolo, offset_Mask):
                iPoints = 2
            elif Mask_rifle10m_1.overlap(MaskDiabolo, offset_Mask):
                iPoints = 1
            elif Mask_rifle10m_0.overlap(MaskDiabolo, offset_Mask):
                iPoints = 0
        # target evaluation rifle 15m
        if xRifle15m:
            if Mask_rifle15m_10.overlap(MaskDiabolo, offset_Mask):
                iPoints = 10
            elif Mask_rifle15m_9.overlap(MaskDiabolo, offset_Mask):
                iPoints = 9
            elif Mask_rifle15m_8.overlap(MaskDiabolo, offset_Mask):
                iPoints = 8
            elif Mask_rifle15m_7.overlap(MaskDiabolo, offset_Mask):
                iPoints = 7
            elif Mask_rifle15m_6.overlap(MaskDiabolo, offset_Mask):
                iPoints = 6
            elif Mask_rifle15m_5.overlap(MaskDiabolo, offset_Mask):
                iPoints = 5
            elif Mask_rifle15m_4.overlap(MaskDiabolo, offset_Mask):
                iPoints = 4
            elif Mask_rifle15m_3.overlap(MaskDiabolo, offset_Mask):
                iPoints = 3
            elif Mask_rifle15m_2.overlap(MaskDiabolo, offset_Mask):
                iPoints = 2
            elif Mask_rifle15m_1.overlap(MaskDiabolo, offset_Mask):
                iPoints = 1
            elif Mask_rifle15m_0.overlap(MaskDiabolo, offset_Mask):
                iPoints = 0
        #target evaluation Biathlon
        if xBiathlon:
            if Mask_Bia_1.overlap(MaskDiabolo, offset_Mask):
                Biathlon_tmpScore[0] = True
            if Mask_Bia_2.overlap(MaskDiabolo, offset_Mask):
                Biathlon_tmpScore[1] = True
            if Mask_Bia_3.overlap(MaskDiabolo, offset_Mask):
                Biathlon_tmpScore[2] = True
            if Mask_Bia_4.overlap(MaskDiabolo, offset_Mask):
                Biathlon_tmpScore[3] = True
            if Mask_Bia_5.overlap(MaskDiabolo, offset_Mask):
                Biathlon_tmpScore[4] = True

    def zeichnen():
        global xBiathlon,iVerticalName,iButtonStatus,xButtonEnter,xPistol10m,xRifle10m,xRifle15m,xBiathlon,xIntro,iCountShots,xSettings,iButtonCount
        global xRoundsSet,xShotsSet,xGameOver,iRoundShotsave,iGlobalRounds,xSetRoundShots,iHorizontalName,iHorizontalLine,iVerticalPoints,iHorizontalPoints
        global iLinePoints,xScoreBoard,itmpGlobalRounds
        screen.fill(FIREARMS)
        iVerticalName = 50
        #Main Menu
        if xIntro:
            screen.blit(pic_pickpistol10m_sc, (300, 250))
            screen.blit(pic_pickrifle10m_sc, (420, 251))
            screen.blit(pic_pickrifle15m_sc, (645, 251))
            screen.blit(pic_Biathlon_sc, (860, 250))
            screen.blit(pic_buttonsettings_sc, (150, 250))

            #Pistol 10m
            if iButtonStatus == 0:
                pygame.draw.rect(screen, RED, [300, 250, 100, 85], 3)
                if xButtonEnter:
                    xPistol10m = True
                    xButtonEnter = False
                    xIntro = False
                    iCountShots = iRoundShotsave
            #Rifle 10m
            if iButtonStatus == 1:
                pygame.draw.rect(screen, RED, [420, 251, 200, 65], 3)
                if xButtonEnter:
                    xRifle10m = True
                    xButtonEnter = False
                    xIntro = False
                    iCountShots = iRoundShotsave
            #Rifle 15m
            if iButtonStatus == 2:
                pygame.draw.rect(screen, RED, [645, 251, 200, 65], 3)
                if xButtonEnter:
                    xRifle15m = True
                    xButtonEnter = False
                    xIntro = False
                    iCountShots = iRoundShotsave
            #Biathlon
            if iButtonStatus == 3:
                pygame.draw.rect(screen, RED, [860, 250, 100, 146], 3)
                if xButtonEnter:
                    xBiathlon = True
                    xButtonEnter = False
                    xIntro = False
                    iCountShots = 5
            #Settings
            if iButtonStatus == -1:
                pygame.draw.rect(screen, RED, [150, 250, 100, 52], 3)
                if xButtonEnter:
                    iButtonStatus = 0
                    xIntro = False
                    xSettings = True
                    xButtonEnter = False

        #Settings
        if xSettings:
            # Hard texting
            screen.fill(FIREARMS)
            txtSettings = GAME_FONT.render("SETTINGS", True, (255, 255, 255))
            screen.blit(txtSettings, (580, 100))
            pygame.draw.line(screen, (255,255,255), [300, 150], [1000, 150], 3)
            txtSettings = GAME_FONT.render("Anzahl Runden:", True, (255, 255, 255))
            screen.blit(txtSettings, (435, 300))
            txtSettings = GAME_FONT.render("Schuss pro Runde:", True, (255, 255, 255))
            screen.blit(txtSettings, (400, 350))

            # Menu texting / blinking
            if xRoundsSet:
                pygame.draw.rect(screen, GREEN, [685, 295, 50, 50], 3)
                if xButtonEnter:
                    RoundHandler()
                    xButtonEnter = False
                    xRoundsSet = False
                if xBlink:
                    iGlobalRounds = iButtonCount
                    txtCount = GAME_FONT.render(str(iGlobalRounds), True, (255, 255, 255))
                    screen.blit(txtCount, (700, 300))
            else:
                txtCount = GAME_FONT.render(str(iGlobalRounds), True, (255, 255, 255))
                screen.blit(txtCount, (700, 300))
            if xShotsSet:
                pygame.draw.rect(screen, GREEN, [685, 345, 50, 50], 3)
                if xButtonEnter:
                    xButtonEnter = False
                    xShotsSet = False
                if xBlink:
                    iRoundShotsave = iButtonCount
                    txtCount = GAME_FONT.render(str(iRoundShotsave), True, (255, 255, 255))
                    screen.blit(txtCount, (700, 350))
                    xSetRoundShots = True
            else:
                txtCount = GAME_FONT.render(str(iRoundShotsave), True, (255, 255, 255))
                screen.blit(txtCount, (700, 350))

            if iButtonStatus == 0 and not xRoundsSet:
                pygame.draw.rect(screen, RED, [685, 295, 50, 50], 3)
                if xButtonEnter:
                    xButtonEnter = False
                    xRoundsSet = True
            if iButtonStatus == 1 and not xShotsSet:
                pygame.draw.rect(screen, RED, [685, 345, 50, 50], 3)
                if xButtonEnter:
                    xButtonEnter = False
                    xShotsSet = True

        #10m Pistole
        if xPistol10m:
            screen.fill(FIREARMS)
            for i in range(0, len(pic_Scheibe_pistol10m)):
                screen.blit(pic_Scheibe_pistol10m[i], (0, 0))
            screen.blit(pic_Pistol_scale, (350, 50))
            txtPlayerNames = GAME_FONT.render("Active Player", True, (240, 255, 240))
            screen.blit(txtPlayerNames, (60, 50))
            pygame.draw.line(screen, (255, 255, 255), [55, 93], [265, 93], 2)
            screen.blit(txtActivePlayer, (60, 100))
            #Player Score
            for i in range(0, len(names)):
                txtPlayerNames = GAME_FONT.render(str(Players[i].name) + ":", True, (240, 255, 240))
                pygame.draw.line(screen, (255, 255, 255), [1050, iVerticalName + 45], [1300, iVerticalName + 45], 1)
                txtPlayerScore = GAME_FONT.render(str(Players[i].score_10mPistol[itmpGlobalRounds]), True, (240, 255, 240))
                screen.blit(txtPlayerNames, (1050, iVerticalName))
                screen.blit(txtPlayerScore, (1050, iVerticalName +50))
                iVerticalName += 100

        #10m Rifle
        if xRifle10m:
            screen.fill(FIREARMS)
            for i in range(0, len(pic_Scheibe_rifle10m)):
                screen.blit(pic_Scheibe_rifle10m[i], (0, 0))
            screen.blit(pic_Rifle_scale, (490, 240))
            txtPlayerNames = GAME_FONT.render("Active Player", True, (240, 255, 240))
            screen.blit(txtPlayerNames, (60, 50))
            pygame.draw.line(screen, (255, 255, 255), [55, 93], [265, 93], 2)
            screen.blit(txtActivePlayer, (60, 100))
            # Player Score
            for i in range(0, len(names)):
                txtPlayerNames = GAME_FONT.render(str(Players[i].name + ":", True, (240, 255, 240)))
                pygame.draw.line(screen, (255, 255, 255), [1050, iVerticalName + 45], [1300, iVerticalName + 45], 1)
                txtPlayerScore = GAME_FONT.render(str(Players[i].score_10mRifle[itmpGlobalRounds]), True, (240, 255, 240))
                screen.blit(txtPlayerNames, (1050, iVerticalName))
                screen.blit(txtPlayerScore, (1050, iVerticalName +50))
                iVerticalName += 100

        #15m Rifle
        if xRifle15m:
            screen.fill(FIREARMS)
            for i in range(0, len(pic_Scheibe_rifle15m)):
                screen.blit(pic_Scheibe_rifle15m[i], (0, 0))
            screen.blit(pic_Rifle15m_scale, (465, 215))
            txtPlayerNames = GAME_FONT.render("Active Player", True, (240, 255, 240))
            screen.blit(txtPlayerNames, (60, 50))
            pygame.draw.line(screen, (255, 255, 255), [55, 93], [265, 93], 2)
            screen.blit(txtActivePlayer, (60, 100))
            # Player Score
            for i in range(0, len(names)):
                txtPlayerNames = GAME_FONT.render(Players[i].name) + ":", True, (240, 255, 240)
                pygame.draw.line(screen, (255, 255, 255), [1050, iVerticalName + 45], [1300, iVerticalName + 45], 1)
                txtPlayerScore = GAME_FONT.render(str(Players[i].score_15mRifle[itmpGlobalRounds]), True, (240, 255, 240))
                screen.blit(txtPlayerNames, (1050, iVerticalName))
                screen.blit(txtPlayerScore, (1050, iVerticalName +50))
                iVerticalName += 100

        #Biathlon
        if xBiathlon:
            screen.fill(FIREARMS)
            # Player Score and Buttons
            for i in range(0, len(names)):
                txtPlayerNames = GAME_FONT.render(str(Players[i].name), True, (240, 255, 240))
                txtPlayerScore = GAME_FONT.render(str(Players[i].score_Biathlon[itmpGlobalRounds]), True, (240, 255, 240))
                screen.blit(txtPlayerNames, (1050, iVerticalName))
                screen.blit(txtPlayerScore, (1050, iVerticalName + 50))
                iVerticalName += 100
            screen.blit(txtActivePlayer, (345, 275))
            screen.blit(pic_Biathlon_Rechteck, (0, 0))
            for i in range(0, len(pic_Biathlon_scheiben)):
                screen.blit(pic_Biathlon_scheiben[i], (0, 0))
                if Biathlon_tmpScore[i]:
                    screen.blit(pic_Biathlon_target[i], (0, 0))

        #GameOver / Stats
        if xGameOver or xScoreBoard:
            screen.fill(FIREARMS)
            txt_Score = SCORE_FONT.render("Score Board:", True, (240, 255, 240))
            screen.blit(txt_Score, (550, 60))
            pygame.draw.line(screen, (255, 255, 255), [50, 120], [1310, 120], 4)
            # Player Score
            for i in range(0, len(names)):
                #basic framework
                pygame.draw.line(screen, (255, 255, 255), [iHorizontalLine, 150], [iHorizontalLine, 750], 2)
                txtPlayerNames = GAME_FONT.render(str(Players[i].name), True, (240, 255, 240))
                screen.blit(txtPlayerNames, (iHorizontalName, 145))
                # 10m Pistol
                screen.blit(pic_PistolScore, (iHorizontalName, 205))
                txtDiscipline = DISCIPLINE_FONT.render("10m", True, (240, 255, 240))
                screen.blit(txtDiscipline, (iHorizontalName, 185))
                # 10m Rifle
                screen.blit(pic_rifle_score, (iHorizontalName + 48, 208))
                txtDiscipline = DISCIPLINE_FONT.render("10m", True, (240, 255, 240))
                screen.blit(txtDiscipline, (iHorizontalName + 48, 185))
                # 15m Rifle
                screen.blit(pic_rifle_score, (iHorizontalName + 100, 208))
                txtDiscipline = DISCIPLINE_FONT.render("15m", True, (240, 255, 240))
                screen.blit(txtDiscipline, (iHorizontalName + 100, 185))
                # Biathlon
                screen.blit(pic_BiathlonScore, (iHorizontalName + 150, 203))
                txtDiscipline = DISCIPLINE_FONT.render("15m", True, (240, 255, 240))
                screen.blit(txtDiscipline, (iHorizontalName + 150, 185))

                iHorizontalPoints += 200
                iVerticalPoints += 50
                iHorizontalName += 200
                iHorizontalLine += 200

            iVerticalPoints = 250
            iHorizontalName = 100
            iHorizontalLine = 95
            iHorizontalPoints = 100
            iLinePoints = 95

            for x in range(0, iGlobalRounds):
                for y in range (0, len(names)):
                    txtPlayerScore = GAME_FONT.render(str(x+1) + ".", True, (240, 255, 240))
                    screen.blit(txtPlayerScore, (60, iVerticalPoints))
                    if Players[y].score_10mPistol[x] == 0:
                        txtPlayerScore = GAME_FONT.render(" -", True, (240, 255, 240))
                    else:
                        txtPlayerScore = GAME_FONT.render(str(Players[y].score_10mPistol[x]), True, (240, 255, 240))
                    screen.blit(txtPlayerScore, (iHorizontalPoints, iVerticalPoints))
                    if Players[y].score_10mRifle[x] == 0:
                        txtPlayerScore = GAME_FONT.render(" -", True, (240, 255, 240))
                    else:
                        txtPlayerScore = GAME_FONT.render(str(Players[y].score_10mRifle[x]), True, (240, 255, 240))
                    screen.blit(txtPlayerScore, (iHorizontalPoints + 50, iVerticalPoints))
                    if Players[y].score_15mRifle[x] == 0:
                        txtPlayerScore = GAME_FONT.render(" -", True, (240, 255, 240))
                    else:
                        txtPlayerScore = GAME_FONT.render(str(Players[y].score_15mRifle[x]), True, (240, 255, 240))
                    screen.blit(txtPlayerScore, (iHorizontalPoints + 100, iVerticalPoints))
                    if Players[y].score_Biathlon[x] == 0:
                        txtPlayerScore = GAME_FONT.render(" -", True, (240, 255, 240))
                    else:
                        txtPlayerScore = GAME_FONT.render(str(Players[y].score_Biathlon[x]), True, (240, 255, 240))
                    screen.blit(txtPlayerScore, (iHorizontalPoints + 150, iVerticalPoints))
                    iHorizontalPoints += 200

                iHorizontalPoints = 100
                iVerticalPoints += 50

    def resetDiabolo():
        global mausx,mausy,Diabolo_Rect,Schuss
        Diabolo_Rect = [0, 0]
        mausx = 0
        mausy = 0

    def ButtonHandler():
        global xIntro,xPistol10m,xRifle10m,xRifle15m,xBiathlon,xReset,xHit,iPoints,iButtonStatus,xButtonEnter,xButtonBack,iButtonCount,xSettings,xGameOver,xScoreBoard,xButtonPressed
        iGetAction = hmsysteme.get_action()
        if iGetAction > 0:
            xButtonPressed = True
            # Reset
            if iGetAction == 1:
                resetStats()
            # +++
            if iGetAction == 2:
                iButtonCount += 1
            # Score Board
            if iGetAction == 3:
                xPistol10m = False
                xRifle10m = False
                xRifle15m = False
                xBiathlon = False
                xIntro = False
                if not xSettings:
                    xScoreBoard = True
            # <<<
            if iGetAction == 4:
                if not iButtonStatus < 0:
                    iButtonStatus -= 1
            # Enter
            if iGetAction == 5:
                xButtonEnter = True
            # >>>
            if iGetAction == 6:
                if not iButtonStatus > 2:
                    iButtonStatus += 1
            # Back
            if iGetAction == 7:
                xIntro = True
                xPistol10m = False
                xRifle10m = False
                xRifle15m = False
                xBiathlon = False
                xSettings = False
                xGameOver = False
                xScoreBoard = False
            # ---
            if iGetAction == 8:
                if iButtonCount > 0:
                    iButtonCount -= 1
            # Button Blind Shot
            if iGetAction == 9:
                xHit = True
                iPoints = 0

    def resetStats():
        global iRound, xGameOver, itmpGlobalRounds, xGameReset, iRoundCount, iCountShots, xInitial
        RoundHandler()
        iRound = 0
        itmpGlobalRounds = 0
        xGameReset = False
        iCountShots = iRoundShotsave
        xInitial = True

    def RoundHandler():
        global iGlobalRounds
        #iRoundCount.clear()
        iRoundCount.append(1)
        for x in range(len(names)):
            Players[x].score_10mPistol.clear()
            Players[x].score_10mRifle.clear()
            Players[x].score_15mRifle.clear()
            Players[x].score_Biathlon.clear()
        for i in range(0, iGlobalRounds):
            for a in range(len(names)):
                Players[a].score_10mPistol.append(0)
                Players[a].score_10mRifle.append(0)
                Players[a].score_15mRifle.append(0)
                Players[a].score_Biathlon.append(0)

    #define masks
    Diabolo = pygame.image.load(os.path.join(path, "pics/Schuss.png"))
    MaskDiabolo = pygame.mask.from_surface(Diabolo)
    Diabolo_Rect = Diabolo.get_rect()

    #Create Playerclasses
    for i in range(0, len(names)):
        Players.append(Player(names[i]))

    #Font
    GAME_FONT = pygame.font.SysFont("Times", 35)
    SCORE_FONT = pygame.font.SysFont("Times", 45)
    DISCIPLINE_FONT = pygame.font.SysFont("Times", 17)
    hit_for_screenshot = False
    font_fade = pygame.USEREVENT + 1
    pygame.time.set_timer(font_fade, 400)

    # Start Game
    while hmsysteme.game_isactive():

        # Check Buttons
        ButtonHandler()
        for event in pygame.event.get():
            # Beenden bei [ESC] oder [X]
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                hit_for_screenshot = True
                mausx = event.pos[0]
                mausy = event.pos[1]
                print("X:", mausx, "Y:", mausy)
                Diabolo_Rect = pygame.Rect(mausx-9, mausy-9, 18, 18)
                screen.blit(Diabolo, Diabolo_Rect)
                if xPistol10m or xRifle10m or xRifle15m or xBiathlon and not xIntro and not xReset:
                    Evaluation()

            if event.type == font_fade:
                xBlink = not xBlink

        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            mausx = pos[0]
            mausy = pos[1]
            Diabolo_Rect = pygame.Rect(pos[0] - 9, pos[1] - 9, 18, 18)
            screen.blit(Diabolo, Diabolo_Rect)

            if xPistol10m or xRifle10m or xRifle15m or xBiathlon and not xIntro and not xReset:
                Evaluation()

        #Active Player
        txtActivePlayer = GAME_FONT.render(str(Players[iRound].name) + ": " + str(iCountShots), True, (255, 255, 255))

        #add points to players and count rounds
        if xSetRoundShots:
            iCountShots = iRoundShotsave
            xSetRoundShots = False
        if not xGameOver and not xSettings:
            if xHit:
                if xPistol10m:
                    Players[iRound].score_10mPistol[itmpGlobalRounds] += iPoints
                if xRifle10m:
                    Players[iRound].score_10mRifle[itmpGlobalRounds] += iPoints
                if xRifle15m:
                    Players[iRound].score_15mRifle[itmpGlobalRounds] += iPoints
                iCountShots -= 1
                xHit = False
                iPoints = 0
            if iCountShots == 0:
                for i in range(0, 5):
                    Players[iRound].score_Biathlon[itmpGlobalRounds] += Biathlon_tmpScore[i]
                    Biathlon_tmpScore[i] = 0
                if xBiathlon:
                   iCountShots = 5
                else:
                    iCountShots = iRoundShotsave
                iRound += 1
            if iRound == len(names):
                iRoundCount.append(1)
                print(iRoundCount)
                itmpGlobalRounds += 1
                iRound = 0
                for i in range(len(names)):
                    Players[i].score_10mPistol.append(0)
                    Players[i].score_10mRifle.append(0)
                    Players[i].score_15mRifle.append(0)
                    Players[i].score_Biathlon.append(0)
            if itmpGlobalRounds == iGlobalRounds and not xGameReset:
                xGameOver = True
                xGameReset = True
                xPistol10m = False
                xRifle10m = False
                xRifle15m = False
                xBiathlon = False

        #Screenshot
        if hit_for_screenshot:
            screen.blit(Diabolo, Diabolo_Rect)
            pygame.display.flip()
            hmsysteme.take_screenshot(screen)
            hit_for_screenshot = False

        zeichnen()
        resetDiabolo()
        xReset = False
        pygame.display.flip()
        if xButtonPressed:
            xButtonPressed = False
            hmsysteme.take_screenshot(screen)
        #initial stuff
        if xInitial:
            RoundHandler()
            xInitial = False
            hmsysteme.take_screenshot(screen)
        clock.tick(framerate)



if __name__ == '__main__':
    main()

