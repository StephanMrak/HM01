
def main():
    global mausx,mausy, ipicture_speed,xColourCont,iColourCount
    global offsetmauler,xhit_mauler,imauler,xmauler_done,imauler2
    global offsetCow,xhit_Cow,iCow,xCow_done,iCow2
    global offsetEarthElement,xhit_EarthElement,iEarthElement,xEarthElement_done,iEarthElement2
    global offsetSwampCreature,xhit_SwampCreature,iSwampCreature,xSwampCreature_done,iSwampCreature2
    global offsetBullrog,xhit_Bullrog,iBullrog,xBullrog_done,iBullrog2
    global offsetMercenary,xhit_Mercenary,iMercenary,xMercenary_done,iMercenary2
    global offsetIcemonster,xhit_Icemonster,iIcemonster,xIcemonster_done,iIcemonster2
    global iTime,iFPS,xGameOver,xStartCounter,listEnemy,xNewTarget,iActiveEnemy,xStartGame,xHit,iTimerNext,iCountNext,iCountTmp,iActivePosi,listPosition
    global xyPosi,xyPosi1,xyPosi2,xyPosi3,xyPosi4,xyPosi5,xyPosi6,xyPosi7
    global PlayerScore,iScoreCounter,iTimeScore
    global txtScore_y,get_yposi,iScoreVisible,txt_ScoreShot,iScoreCalculated
    global iCountScoreTimer,xCountScoreTimer,xtmpHit,xInit
    global timeRndPopUp,iTimeRnd,xInitGame,InitTimeRndPopUp,timeInitPopup,iInitTimePopup
    import pygame
    import time
    import hmsysteme
    import os
    import platform
    import random
    import pygame.freetype
    hmsysteme.put_button_names(["RESET", "+", "SCORE BOARD", "<", "Enter", ">", "BACK", "-", "BLIND SHOT"])
    print(platform.uname())
    pygame.init()

    #size = [1366, 768]
    size = hmsysteme.get_size()

    #Get Playernames
    names = hmsysteme.get_playernames()
    if not names:
        names = ["Stephan", "Marion", "Flori", "Peter Mafai"]

    path = os.path.realpath(__file__)
    #    path = path.replace('Prestige\Prestige.py', '')
    if 'Linux' in platform.uname():
        path = path.replace('ShootUP.py', '')
    else:
        path = path.replace('ShootUP.py', '')

    #screen = pygame.display.set_mode(size)
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    clock = pygame.time.Clock()
    pygame.display.set_caption("ShootUP")

    #Pics
    Diabolo = pygame.image.load(os.path.join(path,"pics/ShootUP/Schuss.png"))
    pic_background = pygame.image.load(os.path.join(path, "pics/ShootUP/backgroundx.jpg"))
    pic_Overlay1 = pygame.image.load(os.path.join(path, "pics/ShootUP/Overlay1.png"))
    pic_Overlay2 = pygame.image.load(os.path.join(path, "pics/ShootUP/Overlay2.png"))

    #Enemy
    pic_Mauler = pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/0.png"))
    pic_Mauler_death = [pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/0.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/1.png")),
                        pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/2.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/3.png")),
                        pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/4.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/5.png")),
                        pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/6.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/7.png")),
                        pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/8.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/9.png")),
                        pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/10.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/11.png")),
                        pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/12.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mauler/Death/13.png"))]

    pic_Cow =     [pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/1.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/2.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/3.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/4.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/5.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/6.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/7.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/8.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/9.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/10.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/11.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/12.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/13.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/14.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/15.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/16.png")),
                     pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/17.png")), pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/18.png")),
                    pygame.image.load(os.path.join(path,"pics/ShootUP/Cow/18.png"))]

    pic_EarthElement =  pygame.image.load(os.path.join(path,"pics/ShootUP/EarthElement/0x.png"))
    pic_EarthElement_death =    [pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/0.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/1.png")),
                                 pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/2.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/3.png")),
                                 pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/4.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/5.png")),
                                 pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/6.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/7.png")),
                                 pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/8.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/9.png")),
                                 pygame.image.load(os.path.join(path, "pics/ShootUP/EarthElement/Death/10.png"))]

    pic_SwampCreature = pygame.image.load(os.path.join(path,"pics/ShootUP/SwampCreature/0.png"))
    pic_SwampCreature_death =   [pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/0.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/1.png")),
                            pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/2.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/3.png")),
                            pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/4.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/5.png")),
                            pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/6.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/7.png")),
                            pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/8.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/9.png")),
                            pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/10.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/11.png")),
                            pygame.image.load(os.path.join(path, "pics/ShootUP/SwampCreature/Death/12.png"))]

    pic_Bullrog = pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/0.png"))
    pic_Bullrog_death = [pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/0.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/1.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/2.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/3.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/4.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/5.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/6.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/7.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/8.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/9.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/10.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/11.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/12.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/13.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/14.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/15.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/16.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/17.png")),
                         pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/18.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Ballrog/Death/19.png"))]

    pic_Mercenary = pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/0.png"))
    pic_Mercenary_death = [pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/1.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/2.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/3.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/4.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/5.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/6.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/7.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/8.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/9.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/10.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Mercenary/Death/11.png"))]
    pic_Icemonster = pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/0.png"))
    pic_Icemonster_death = [pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/1.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/2.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/3.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/4.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/5.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/6.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/7.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/8.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/9.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/10.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/11.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/12.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/13.png")), pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/14.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/15.png")),pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/16.png")),
                           pygame.image.load(os.path.join(path, "pics/ShootUP/Icemonster/Death/17.png"))]

    ############Variablen###########
    BLACK = (0, 0, 0)
    framerate = 30
    mausx = 0
    mausy = 0
    ipicture_speed = 2
    GAME_FONT = pygame.font.SysFont("Times", 60)
    SCORE_FONT = pygame.font.SysFont("Comic Sans MS", 40,True)
    txt_ScoreShot = SCORE_FONT.render("+10", True, (0, 240, 0))
    hit_for_screenshot = False
    offsetDiabolo = 9
    iTime = 20
    iFPS = 0
    xGameOver = False
    xStartCounter = False
    #1=Cow;2=Mauler;3=EarthElement;4=SwampCreature;5=Bullrog;6=Mercenary;7=Icemonster
    listEnemy = [1,2,3,4,5,6,7]
    iActiveEnemy = 0
    listPosition = [1,2,3,4,5,6]
    iActivePosi = 0
    xyPosi = [0,0]
    xyPosi1 = [800,150]
    xyPosi2 = [750,210]
    xyPosi3 = [400,290]
    xyPosi4 = [650,250]
    xyPosi5 = [650,150]
    xyPosi6 = [300,150]
    xyPosi7 = [750,400]
    xNewTarget = False
    xStartGame = False
    xHit = False
    iTimerNext = 30
    iCountNext = 0
    iCountTmp = 0
    PlayerScore = 0
    iScoreCounter = 0
    txtScore_y = 0
    get_yposi = False
    iScoreVisible = 0
    xColourCont = False
    iColourCount = 0
    iCountScoreTimer = 0
    xCountScoreTimer = False
    iTimeScore = 0
    xtmpHit = False
    xInit = True
    InitTimeRndPopUp = [90,120,150,180]
    timeRndPopUp = [100,110,120,130,140,150]
    iTimeRnd = 0
    xInitGame = True
    timeInitPopup = 0
    iInitTimePopup = 0
    iScoreCalculated = 0

    #Mauler
    offsetmauler = 0
    xhit_mauler = False
    imauler = 0
    xmauler_done = False
    imauler2 = 2

    #Cow
    offsetCow = 0
    xhit_Cow = False
    iCow = 0
    iCow2 = 2
    xCow_done = False

    #EarthElement
    offsetEarthElement = 0
    xhit_EarthElement = False
    iEarthElement = 0
    iEarthElement2 = 2
    xEarthElement_done = False

    #SwampCreature
    offsetSwampCreature = 0
    xhit_SwampCreature = False
    iSwampCreature = 0
    iSwampCreature2 = 2
    xSwampCreature_done = False

    #Bullrog
    offsetBullrog = 0
    xhit_Bullrog = False
    iBullrog = 0
    iBullrog2 = 2
    xBullrog_done = False

    #Mercenary
    offsetMercenary = 0
    xhit_Mercenary = False
    iMercenary = 0
    iMercenary2 = 2
    xMercenary_done = False

    #Icemonster
    offsetIcemonster = 0
    xhit_Icemonster = False
    iIcemonster = 0
    iIcemonster2 = 2
    xIcemonster_done = False


    class Player:
        def __init__(self, name, score, timescore):
            self.name = name
            self.score = score
            self.timescore = timescore

    def zeichnen():
        global imauler,xmauler_done,imauler2
        global iCow, xCow_done, iCow2, xhit_Cow
        global iSwampCreature, xSwampCreature_done, iSwampCreature2, xhit_SwampCreature
        global iEarthElement, xEarthElement_done, iEarthElement2, xhit_EarthElement
        global iBullrog, xBullrog_done, iBullrog2,xhit_Bullrog
        global iMercenary, xMercenary_done, iMercenary2, xhit_Mercenary
        global iIcemonster, xIcemonster_done, iIcemonster2, xhit_Icemonster
        global iTime,iFPS,xGameOver,iActiveEnemy,xStartCounter,iCountTmp,iCountNext,iTimerNext,xNewTarget
        global xyPosi,iActivePosi,xyPosi1,xyPosi2,xyPosi3,xyPosi4,xyPosi5,xyPosi6,xyPosi7
        global iCountScoreTimer,xCountScoreTimer,iTimeRnd,iScoreCalculated,txtScore_y,get_yposi,iScoreVisible,txt_ScoreShot

        #Active Position
        if iActivePosi == 1:
            xyPosi = xyPosi1
        if iActivePosi == 2:
            xyPosi = xyPosi2
        if iActivePosi == 3:
            xyPosi = xyPosi3
        if iActivePosi == 4:
            xyPosi = xyPosi4
        if iActivePosi == 5:
            xyPosi = xyPosi5
        if iActivePosi == 6:
            xyPosi = xyPosi6
        if iActivePosi == 7:
            xyPosi = xyPosi7

        ##### Background #######
        screen.blit(pic_background, (0, 0))
        if not xGameOver:
            # CountDown
            if xStartCounter:
                iFPS += 1
                if iFPS >= 30:
                    iTime -= 1
                    iFPS = 0

            #txt_CountDown = GAME_FONT.render(str(iTime), True, (255, 255, 255))
            #screen.blit(txt_CountDown, (80, 60))

            if iActiveEnemy == 1:
                #Cow
                if not xhit_Cow:
                    screen.blit(pic_Cow[0], xyPosi)
                else:
                    screen.blit(pic_Cow[18], xyPosi)
                    if not xCow_done:
                        screen.blit(pic_Cow[iCow], xyPosi)
                        iCow2 += 1
                        if iCow2 > ipicture_speed:
                            iCow2 = 0
                            iCow += 1
                            if iCow > 18:
                                xCow_done = True
                    else:
                        screen.blit(pic_Cow[18], xyPosi)
                if xhit_Cow:
                    if get_yposi:
                        get_yposi = False
                        txtScore_y = xyPosi[1]
                    iScoreVisible += 1
                    if iScoreVisible < 40:
                        screen.blit(txt_ScoreShot, (xyPosi[0] + 40, txtScore_y))
                        txtScore_y = txtScore_y - 3
                    iCountTmp += 1
                    if iCountTmp >= 3:
                        iCountNext += 1
                        iCountTmp = 0
                    if iCountNext >= iTimeRnd:
                        xNewTarget = True
                        iCountNext = 0

            if iActiveEnemy == 2:
                #Mauler
                if not xhit_mauler:
                    screen.blit(pic_Mauler, xyPosi)
                else:
                    if not xmauler_done:
                        screen.blit(pic_Mauler_death[imauler], xyPosi)
                        imauler2 += 1
                        if imauler2 > ipicture_speed:
                            imauler2 = 0
                            imauler += 1
                            if imauler > 12:
                                xmauler_done = True
                    else:
                        screen.blit(pic_Mauler_death[12], xyPosi)
                if xhit_mauler:
                    if get_yposi:
                        get_yposi = False
                        txtScore_y = xyPosi[1]
                    iScoreVisible += 1
                    if iScoreVisible < 40:
                        screen.blit(txt_ScoreShot, (xyPosi[0] + 40, txtScore_y))
                        txtScore_y = txtScore_y - 3
                    iCountTmp += 1
                    if iCountTmp >= 3:
                        iCountNext += 1
                        iCountTmp = 0
                    if iCountNext >= iTimeRnd:
                        xNewTarget = True
                        iCountNext = 0

            #EarthElement
            if iActiveEnemy == 3:
                if not xhit_EarthElement:
                    screen.blit(pic_EarthElement, xyPosi)
                else:
                    if not xEarthElement_done:
                        screen.blit(pic_EarthElement_death[iEarthElement], xyPosi)
                        iEarthElement2 += 1
                        if iEarthElement2 > ipicture_speed:
                            iEarthElement2 = 0
                            iEarthElement += 1
                            if iEarthElement > 10:
                                xEarthElement_done = True
                    else:
                        screen.blit(pic_EarthElement_death[10], xyPosi)
                if xhit_EarthElement:
                    if get_yposi:
                        get_yposi = False
                        txtScore_y = xyPosi[1]
                    iScoreVisible += 1
                    if iScoreVisible < 40:
                        screen.blit(txt_ScoreShot, (xyPosi[0] + 40, txtScore_y))
                        txtScore_y = txtScore_y - 3
                    iCountTmp += 1
                    if iCountTmp >= 3:
                        iCountNext += 1
                        iCountTmp = 0
                    if iCountNext >= iTimeRnd:
                        xNewTarget = True
                        iCountNext = 0

            #SwampCreature
            if iActiveEnemy == 4:
                if not xhit_SwampCreature:
                    screen.blit(pic_SwampCreature, xyPosi)
                else:
                    if not xSwampCreature_done:
                        screen.blit(pic_SwampCreature_death[iSwampCreature], xyPosi)
                        iSwampCreature2 += 1
                        if iSwampCreature2 > ipicture_speed:
                            iSwampCreature2 = 0
                            iSwampCreature += 1
                            if iSwampCreature > 12:
                                xSwampCreature_done = True
                    else:
                        screen.blit(pic_SwampCreature_death[12], xyPosi)
                if xhit_SwampCreature:
                    if get_yposi:
                        get_yposi = False
                        txtScore_y = xyPosi[1]
                    iScoreVisible += 1
                    if iScoreVisible < 40:
                        screen.blit(txt_ScoreShot, (xyPosi[0] + 40, txtScore_y))
                        txtScore_y = txtScore_y - 3
                    iCountTmp += 1
                    if iCountTmp >= 3:
                        iCountNext += 1
                        iCountTmp = 0
                    if iCountNext >= iTimeRnd:
                        xNewTarget = True
                        iCountNext = 0

            #Bullrog
            if iActiveEnemy == 5:
                if not xhit_Bullrog:
                    screen.blit(pic_Bullrog, xyPosi)
                else:
                    if not xBullrog_done:
                        screen.blit(pic_Bullrog_death[iBullrog], xyPosi)
                        iBullrog2 += 1
                        if iBullrog2 > ipicture_speed:
                            iBullrog2 = 0
                            iBullrog += 1
                            if iBullrog > 19:
                                xBullrog_done = True
                    else:
                        screen.blit(pic_Bullrog_death[19], xyPosi)
                if xhit_Bullrog:
                    if get_yposi:
                        get_yposi = False
                        txtScore_y = xyPosi[1]
                    iScoreVisible += 1
                    if iScoreVisible < 40:
                        screen.blit(txt_ScoreShot, (xyPosi[0] + 40, txtScore_y))
                        txtScore_y = txtScore_y - 3
                    iCountTmp += 1
                    if iCountTmp >= 3:
                        iCountNext += 1
                        iCountTmp = 0
                    if iCountNext >= iTimeRnd:
                        xNewTarget = True
                        iCountNext = 0

            #Mercenary
            if iActiveEnemy == 6:
                if not xhit_Mercenary:
                    screen.blit(pic_Mercenary, xyPosi)
                else:
                    if not xMercenary_done:
                        screen.blit(pic_Mercenary_death[iMercenary], xyPosi)
                        iMercenary2 += 1
                        if iMercenary2 > ipicture_speed:
                            iMercenary2 = 0
                            iMercenary += 1
                            if iMercenary > 10:
                                xMercenary_done = True
                    else:
                        screen.blit(pic_Mercenary_death[10], xyPosi)
                if xhit_Mercenary:
                    if get_yposi:
                        get_yposi = False
                        txtScore_y = xyPosi[1]
                    iScoreVisible += 1
                    if iScoreVisible < 40:
                        screen.blit(txt_ScoreShot, (xyPosi[0] + 40, txtScore_y))
                        txtScore_y = txtScore_y - 3
                    iCountTmp += 1
                    if iCountTmp >= 3:
                        iCountNext += 1
                        iCountTmp = 0
                    if iCountNext >= iTimeRnd:
                        xNewTarget = True
                        iCountNext = 0

            #Icemonster
            if iActiveEnemy == 7:
                if not xhit_Icemonster:
                    screen.blit(pic_Icemonster, xyPosi)
                else:
                    if not xIcemonster_done:
                        screen.blit(pic_Icemonster_death[iIcemonster], xyPosi)
                        iIcemonster2 += 1
                        if iIcemonster2 > ipicture_speed:
                            iIcemonster2 = 0
                            iIcemonster += 1
                            if iIcemonster > 16:
                                xIcemonster_done = True
                    else:
                        screen.blit(pic_Icemonster_death[16], xyPosi)
                if xhit_Icemonster:
                    if get_yposi:
                        get_yposi = False
                        txtScore_y = xyPosi[1]
                    iScoreVisible += 1
                    if iScoreVisible < 40:
                        screen.blit(txt_ScoreShot, (xyPosi[0] + 40, txtScore_y))
                        txtScore_y = txtScore_y - 3
                    iCountTmp += 1
                    if iCountTmp >= 3:
                        iCountNext += 1
                        iCountTmp = 0
                    if iCountNext >= iTimeRnd:
                        xNewTarget = True
                        iCountNext = 0

            screen.blit(pic_Overlay1, (0, 0))

        else:#GameOver
            screen.fill(BLACK)
            iScoreCalculated = iCountScoreTimer / 30
            iScoreCalculated = int(1 / iScoreCalculated * 10000)
            txt_Score = GAME_FONT.render("Score: " + str(iScoreCalculated), True, (255, 255, 255))
            screen.blit(txt_Score, (500, 250))


        pygame.display.flip()


    def Evaluation():
        global xHit,xhit_mauler,xhit_Cow,xhit_EarthElement,xhit_SwampCreature,xhit_Bullrog,xhit_Mercenary,xhit_Icemonster
        global mausx,mausy,PlayerScore,get_yposi,iScoreVisible,xColourCont,iActiveEnemy,xyPosi
        global iCountScoreTimer,xCountScoreTimer,xtmpHit,iTimeScore,xInit

        MaskDiabolo = pygame.mask.from_surface(Diabolo)
        if iActiveEnemy == 1:
            offsetCow = ((mausx - (xyPosi[0] + offsetDiabolo)), int(mausy - (xyPosi[1] + offsetDiabolo)))
            if mask_Cow.overlap(MaskDiabolo, offsetCow):
                PlayerScore += 10
                xhit_Cow = True
                xHit = True

        if iActiveEnemy == 2:
            offsetmauler = ((mausx - (xyPosi[0] + offsetDiabolo)), int(mausy - (xyPosi[1] + offsetDiabolo)))
            if mask_mauler.overlap(MaskDiabolo, offsetmauler):
                PlayerScore += 10
                xhit_mauler = True
                xHit = True

        if iActiveEnemy == 3:
            offsetEarthElement = ((mausx - (xyPosi[0] + offsetDiabolo)), int(mausy - (xyPosi[1] + offsetDiabolo)))
            if mask_EarthElement.overlap(MaskDiabolo, offsetEarthElement):
                PlayerScore += 10
                xhit_EarthElement = True
                xHit = True

        if iActiveEnemy == 4:
            offsetSwampCreature = ((mausx - (xyPosi[0] + offsetDiabolo)), int(mausy - (xyPosi[1] + offsetDiabolo)))
            if mask_SwampCreature.overlap(MaskDiabolo, offsetSwampCreature):
                PlayerScore += 10
                xhit_SwampCreature = True
                xHit = True

        if iActiveEnemy == 5:
            offsetBullrog = ((mausx - (xyPosi[0] + offsetDiabolo)), int(mausy - (xyPosi[1] + offsetDiabolo)))
            if mask_Bullrog.overlap(MaskDiabolo, offsetBullrog):
                PlayerScore += 10
                xhit_Bullrog = True
                xHit = True

        if iActiveEnemy == 6:
            offsetMercenary = ((mausx - (xyPosi[0] + offsetDiabolo)), int(mausy - (xyPosi[1] + offsetDiabolo)))
            if mask_Mercenary.overlap(MaskDiabolo, offsetMercenary):
                PlayerScore += 10
                xhit_Mercenary = True
                xHit = True

        if iActiveEnemy == 7:
            offsetIcemonster = ((mausx - (xyPosi[0] + offsetDiabolo)), int(mausy - (xyPosi[1] + offsetDiabolo)))
            if mask_Icemonster.overlap(MaskDiabolo, offsetIcemonster):
                PlayerScore += 10
                xhit_Icemonster = True
                xHit = True

        if xHit:
            xInit = False
            iTimeScore = iTimeScore + iCountScoreTimer
            print(iTimeScore)
            xtmpHit = False
            xColourCont = True
            hmsysteme.put_rgbcolor((0, 255, 0))
            get_yposi = True
            iScoreVisible = 0
        else:
            xColourCont = True
            hmsysteme.put_rgbcolor((255, 0, 0))

    def reset_parameter():
        global Diabolo_Rect,mausx,mausy
        global xhit_mauler,xhit_Cow,xhit_EarthElement,xhit_SwampCreature,xhit_Bullrog,xhit_Mercenary,xhit_Icemonster
        Diabolo_Rect = [-20, -20]
        mausx = 0
        mausy = 0


    ###########define masks############
    mask_mauler = pygame.mask.from_surface(pic_Mauler)
    mask_Cow = pygame.mask.from_surface(pic_Cow[0])
    mask_EarthElement = pygame.mask.from_surface(pic_EarthElement)
    mask_SwampCreature = pygame.mask.from_surface(pic_SwampCreature)
    mask_Bullrog = pygame.mask.from_surface(pic_Bullrog)
    mask_Mercenary = pygame.mask.from_surface(pic_Mercenary)
    mask_Icemonster = pygame.mask.from_surface(pic_Icemonster)
    # Start Game
    while hmsysteme.game_isactive():

        # The Game
        if xInitGame:
            timeInitPopup = random.choice(InitTimeRndPopUp)
            xInitGame = False
            xNewTarget = True
        if iInitTimePopup < timeInitPopup:
            iInitTimePopup += 1
        else:
            if xHit:
                xStartCounter = True
                xHit = False

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

                    #Calculate Shot
                    Evaluation()

            if hmsysteme.hit_detected():
                hit_for_screenshot = True
                pos = hmsysteme.get_pos()
                mausx = pos[0]
                mausy = pos[1]
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
                screen.blit(Diabolo, Diabolo_Rect)
                # Calculate Shot
                Evaluation()

            # Screenshot
            if hit_for_screenshot:
                screen.blit(Diabolo, Diabolo_Rect)
                pygame.display.flip()
                hmsysteme.take_screenshot(screen)
                hit_for_screenshot = False

            if xNewTarget:
                hmsysteme.put_rgbcolor((140, 0, 140))
                xColourCont = True
                iTimeRnd = random.choice(timeRndPopUp)
                iActiveEnemy = random.choice(listEnemy)
                iActivePosi = random.choice(listPosition)
                if len(listEnemy) > 1:
                    listEnemy.remove(iActiveEnemy)
                if len(listPosition) > 1:
                    listPosition.remove(iActivePosi)
                else:
                    xGameOver = True
                xNewTarget = False
                if not xInit:
                    xtmpHit = True


            if xtmpHit and not xGameOver:
                print("hochzaehlen")
                iCountScoreTimer += 1

            if xColourCont:
                iColourCount += 1
                if iColourCount == 30:
                    hmsysteme.put_rgbcolor((0, 0, 0))
                    xColourCont = False
                    iColourCount = 0
        #Zeichnen
        zeichnen()
        clock.tick(framerate)

if __name__ == '__main__':
    main()


