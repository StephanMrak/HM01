
def main():
    global mausx,mausy,hit_for_screenshot,offsetDiabolo
    global jackfruit_hit,stinkfrucht_hit,ananas_hit,sauersack_hit,kiwi_hit,birne_hit,banane_hit,apfel_hit,orange_hit,himbeere_hit,kirsche_hit,brombeere_hit,erdbeere_hit
    global jackfruit_done,stinkfrucht_done,ananas_done,sauersack_done,kiwi_done,birne_done,banane_done,apfel_done,orange_done,himbeere_done,kirsche_done,brombeere_done,erdbeere_done
    global yJackFruit,ystinkfrucht,yananas,ysauersack,ykiwi,ybirne,ybanane,yapfel,yorange,yhimbeere,ykirsche,ybrombeere,yerdbeere
    global xResetFruits,iTmpCount,xHitColour,iActivePlayer,tmpListActivePlayer,ListActivePlayer,xInitGame,xFinalshootout,iTmpList,xWin,iColourCount,xCoulourStart

    import pygame
    import time
    import hmsysteme
    import os
    import platform
    import random
    import pygame.freetype
    hmsysteme.put_button_names(["x", "x", "x", "x", "x", "x", "x", "x", "x"])
    print(platform.uname())
    pygame.init()

    #size = [1366, 768]
    size = hmsysteme.get_size()

    #Get Playernames
    names = hmsysteme.get_playernames()
    if not names:
        #names = ["Player 1", "Player 2", "Player 3", "Player 4"]
        names = ["Stephan", "Marion", "Florian", "Peter Mafai"]

    path = os.path.realpath(__file__)
    #    path = path.replace('Prestige\Prestige.py', '')
    if 'Linux' in platform.uname():
        path = path.replace('Elimination.py', '')
    else:
        path = path.replace('Elimination.py', '')

    #screen = pygame.display.set_mode(size)
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    clock = pygame.time.Clock()
    pygame.display.set_caption("Elimination")

    #Pics
    Diabolo = pygame.image.load(os.path.join(path,"pics/Schuss.png"))
    Tree = pygame.image.load(os.path.join(path,"pics/Elimination/Baum.png"))
    JackFruit_origin = pygame.image.load(os.path.join(path,"pics/Elimination/Groß/Jackfruitx.png"))
    Sauersack_origin = pygame.image.load(os.path.join(path,"pics/Elimination/Groß/Sauersackx.png"))
    Stinkfrucht_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Groß/Stinkfruchtx.png"))
    Ananas_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Groß/Ananas.png"))
    Banane_origin = pygame.image.load(os.path.join(path,"pics/Elimination/Mittel/Bananen.png"))
    Apfel_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Mittel/Apfel.png"))
    Birne_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Mittel/Birne.png"))
    Kiwi_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Mittel/Kiwi.png"))
    Himbeere_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Klein/Himbeere.png"))
    Kirsche_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Klein/Kirsche.png"))
    Orange_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Mittel/Orange.png"))
    Brombeere_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Klein/Brombeere.png"))
    Erdbeere_origin = pygame.image.load(os.path.join(path, "pics/Elimination/Klein/Erdbeere.png"))
    JackFruit = pygame.transform.scale(JackFruit_origin, (110,159))
    Sauersack = pygame.transform.scale(Sauersack_origin, (110, 177))
    Stinkfrucht = pygame.transform.scale(Stinkfrucht_origin, (110, 167))
    Bananen = pygame.transform.scale(Banane_origin, (110, 99))
    Apfel = pygame.transform.scale(Apfel_origin, (70, 87))
    Birne = pygame.transform.scale(Birne_origin, (70, 86))
    Himbeere = pygame.transform.scale(Himbeere_origin, (40, 50))
    Kirsche = pygame.transform.scale(Kirsche_origin, (50, 51))
    Kiwi = pygame.transform.scale(Kiwi_origin, (80, 73))
    Ananas = pygame.transform.scale(Ananas_origin, (110, 192))
    Orange = pygame.transform.scale(Orange_origin, (85, 73))
    Brombeere = pygame.transform.scale(Brombeere_origin, (60, 77))
    Erdbeere = pygame.transform.scale(Erdbeere_origin, (60, 87))

    ############Variablen###########
    HIMMELBLAU = (120, 210, 255)
    BLACK = (0,0,0)
    framerate = 30
    mausx = 0
    mausy = 0
    hit_for_screenshot = False
    offsetDiabolo = 9
    jackfruit_hit = False
    jackfruit_done = False
    stinkfrucht_hit = False
    stinkfrucht_done = False
    ananas_done = False
    ananas_hit = False
    sauersack_hit = False
    sauersack_done = False
    kiwi_hit = False
    kiwi_done = False
    birne_hit = False
    birne_done = False
    banane_hit = False
    banane_done = False
    apfel_hit = False
    apfel_done = False
    orange_hit = False
    orange_done = False
    himbeere_hit = False
    himbeere_done = False
    kirsche_hit = False
    kirsche_done = False
    brombeere_hit = False
    brombeere_done = False
    erdbeere_hit = False
    erdbeere_done = False
    yJackFruit = 410
    ystinkfrucht = 470
    yananas = 430
    ysauersack = 410
    ykiwi = 310
    ybirne = 310
    ybanane = 250
    yapfel = 260
    yorange = 310
    yhimbeere = 150
    ykirsche = 150
    ybrombeere = 170
    yerdbeere = 160
    xResetFruits = False
    iTmpCount = 0
    Players = []
    xHitColour = False
    iActivePlayer = 0
    tmpListActivePlayer = []
    ListActivePlayer = []
    xInitGame = True
    xFinalshootout = False
    iTmpList = 0
    xWin = False
    iColourCount = 0
    xCoulourStart = False

    #Fonts
    GAME_FONT = pygame.font.SysFont("Times", 55)
    WIN_FONT = pygame.font.SysFont("Times", 85)
    class Player():
        def __init__(self, name):
            self.name = name



    def zeichnen():
        global jackfruit_done,stinkfrucht_done,ananas_done,sauersack_done,kiwi_done,birne_done,banane_done,apfel_done,orange_done,himbeere_done,kirsche_done,brombeere_done,erdbeere_done
        global yJackFruit,ystinkfrucht,yananas,ysauersack,ykiwi,ybirne,ybanane,yapfel,yorange,yhimbeere,ykirsche,ybrombeere,yerdbeere
        global iActivePlayer,ListActivePlayer,xWin

        if not xWin:
            ##### Background #######
            screen.fill(BLACK)
            screen.blit(Tree,(0,0))

            #Aktiver Spieler
            txtActivePlayer = GAME_FONT.render(str(ListActivePlayer[iActivePlayer]), True, (255, 255, 255))
            screen.blit(txtActivePlayer, (100, 100))

            if not jackfruit_done:
                if not jackfruit_hit:
                    screen.blit(JackFruit, (350, 410))
                else:
                    screen.blit(JackFruit, (350, yJackFruit))
                    yJackFruit += 8
                    if yJackFruit > 800:
                        jackfruit_done = True

            if not stinkfrucht_done:
                if not stinkfrucht_hit:
                    screen.blit(Stinkfrucht, (550, 470))
                else:
                    screen.blit(Stinkfrucht, (550, ystinkfrucht))
                    ystinkfrucht += 8
                    if ystinkfrucht > 800:
                        stinkfrucht_done = True

            if not ananas_done:
                if not ananas_hit:
                    screen.blit(Ananas, (750, 430))
                else:
                    screen.blit(Ananas, (750, yananas))
                    yananas += 8
                    if yananas > 800:
                        ananas_done = True
            if not sauersack_done:
                if not sauersack_hit:
                    screen.blit(Sauersack, (950, 410))
                else:
                    screen.blit(Sauersack, (950, ysauersack))
                    ysauersack += 8
                    if ysauersack > 800:
                        sauersack_done = True
            if not kiwi_done:
                if not kiwi_hit:
                    screen.blit(Kiwi, (510, 310))
                else:
                    screen.blit(Kiwi, (510, ykiwi))
                    ykiwi += 8
                    if ykiwi > 800:
                        kiwi_done = True
            if not birne_done:
                if not birne_hit:
                    screen.blit(Birne, (660, 310))
                else:
                    screen.blit(Birne, (660, ybirne))
                    ybirne += 8
                    if ybirne > 800:
                        birne_done = True
            if not banane_done:
                if not banane_hit:
                    screen.blit(Bananen, (360, 250))
                else:
                    screen.blit(Bananen, (360, ybanane))
                    ybanane += 8
                    if ybanane > 800:
                        banane_done = True
            if not apfel_done:
                if not apfel_hit:
                    screen.blit(Apfel, (940, 260))
                else:
                    screen.blit(Apfel, (940, yapfel))
                    yapfel += 8
                    if yapfel > 800:
                        apfel_done = True
            if not orange_done:
                if not orange_hit:
                    screen.blit(Orange, (790, 310))
                else:
                    screen.blit(Orange, (790, yorange))
                    yorange += 8
                    if yorange > 800:
                        orange_done = True
            if not himbeere_done:
                if not himbeere_hit:
                    screen.blit(Himbeere, (750, 150))
                else:
                    screen.blit(Himbeere, (750, yhimbeere))
                    yhimbeere += 8
                    if yhimbeere > 800:
                        himbeere_done = True
            if not kirsche_done:
                if not kirsche_hit:
                    screen.blit(Kirsche, (630, 150))
                else:
                    screen.blit(Kirsche, (630, ykirsche))
                    ykirsche += 8
                    if ykirsche > 800:
                        kirsche_done = True
            if not brombeere_done:
                if not brombeere_hit:
                    screen.blit(Brombeere, (850, 170))
                else:
                    screen.blit(Brombeere, (850, ybrombeere))
                    ybrombeere += 8
                    if ybrombeere > 800:
                        brombeere_done = True
            if not erdbeere_done:
                if not erdbeere_hit:
                    screen.blit(Erdbeere, (510, 160))
                else:
                    screen.blit(Erdbeere, (510, yerdbeere))
                    yerdbeere += 8
                    if yerdbeere > 800:
                        erdbeere_done = True
        else:
            screen.fill(BLACK)
            txtWinner = WIN_FONT.render("Winner:", True, (255, 255, 255))
            screen.blit(txtWinner, (540, 200))
            txtActivePlayer = WIN_FONT.render(str(ListActivePlayer[iActivePlayer]), True, (255, 255, 255))
            screen.blit(txtActivePlayer, (540, 300))

        pygame.display.flip()


    def Evaluation():
        global mausx,mausy,offsetDiabolo,xHitColour
        global jackfruit_hit,stinkfrucht_hit,ananas_hit,sauersack_hit,kiwi_hit,birne_hit,banane_hit,apfel_hit,orange_hit,himbeere_hit,kirsche_hit,brombeere_hit,erdbeere_hit
        global tmpListActivePlayer,iActivePlayer,xFinalshootout,iTmpList,xWin,xCoulourStart

        xHitColour = False

        offset_jackfruit = ((mausx - (350 + offsetDiabolo)), int(mausy - (410 + offsetDiabolo)))
        if mask_jackfruit.overlap(mask_diabolo, offset_jackfruit):
            jackfruit_hit = True
            xHitColour = True
        offset_stinkfrucht = ((mausx - (550 + offsetDiabolo)), int(mausy - (470 + offsetDiabolo)))
        if mask_stinkfrucht.overlap(mask_diabolo, offset_stinkfrucht):
            stinkfrucht_hit = True
            xHitColour = True
        offset_ananas = ((mausx - (750 + offsetDiabolo)), int(mausy - (430 + offsetDiabolo)))
        if mask_ananas.overlap(mask_diabolo, offset_ananas):
            ananas_hit = True
            xHitColour = True
        offset_sauersack = ((mausx - (950 + offsetDiabolo)), int(mausy - (410 + offsetDiabolo)))
        if mask_sauersack.overlap(mask_diabolo, offset_sauersack):
            sauersack_hit = True
            xHitColour = True
        offset_kiwi = ((mausx - (510 + offsetDiabolo)), int(mausy - (310 + offsetDiabolo)))
        if mask_kiwi.overlap(mask_diabolo, offset_kiwi):
            kiwi_hit = True
            xHitColour = True
        offset_birne = ((mausx - (660 + offsetDiabolo)), int(mausy - (310 + offsetDiabolo)))
        if mask_birne.overlap(mask_diabolo, offset_birne):
            birne_hit = True
            xHitColour = True
        offset_banane = ((mausx - (360 + offsetDiabolo)), int(mausy - (250 + offsetDiabolo)))
        if mask_bananen.overlap(mask_diabolo, offset_banane):
            banane_hit = True
            xHitColour = True
        offset_apfel = ((mausx - (940 + offsetDiabolo)), int(mausy - (260 + offsetDiabolo)))
        if mask_apfel.overlap(mask_diabolo, offset_apfel):
            apfel_hit = True
            xHitColour = True
        offset_orange = ((mausx - (790 + offsetDiabolo)), int(mausy - (310 + offsetDiabolo)))
        if mask_orange.overlap(mask_diabolo, offset_orange):
            orange_hit = True
            xHitColour = True
        offset_himbeere = ((mausx - (750 + offsetDiabolo)), int(mausy - (150 + offsetDiabolo)))
        if mask_himbeere.overlap(mask_diabolo, offset_himbeere):
            himbeere_hit = True
            xHitColour = True
        offset_kirsche = ((mausx - (630 + offsetDiabolo)), int(mausy - (150 + offsetDiabolo)))
        if mask_kirsche.overlap(mask_diabolo, offset_kirsche):
            kirsche_hit = True
            xHitColour = True
        offset_brombeere = ((mausx - (850 + offsetDiabolo)), int(mausy - (170 + offsetDiabolo)))
        if mask_Brombeere.overlap(mask_diabolo, offset_brombeere):
            brombeere_hit = True
            xHitColour = True
        offset_erdbeere = ((mausx - (510 + offsetDiabolo)), int(mausy - (160 + offsetDiabolo)))
        if mask_erdbeere.overlap(mask_diabolo, offset_erdbeere):
            erdbeere_hit = True
            xHitColour = True

        if xHitColour:
            xCoulourStart = True
            hmsysteme.put_rgbcolor((0, 255, 0))
            tmpListActivePlayer[iActivePlayer] = True
            if iActivePlayer < len(ListActivePlayer):
                iActivePlayer += 1
            else:
                iActivePlayer = 0
        else:
            xCoulourStart = True
            hmsysteme.put_rgbcolor((255, 0, 0))
            print("nicht getroffen:" + str(iActivePlayer))
            tmpListActivePlayer[iActivePlayer] = False
            if iActivePlayer < len(ListActivePlayer):
                iActivePlayer += 1
            else:
                iActivePlayer = 0

        #next round
        if iActivePlayer == len(ListActivePlayer):
            print("last Player done")
            for i in range(0, len(tmpListActivePlayer)):
                if not tmpListActivePlayer[i]:
                    if not xFinalshootout:
                        print("löschen: " + str(i))
                        del ListActivePlayer[i]
                    else:
                        if tmpListActivePlayer[0] and not tmpListActivePlayer[1]:
                            del ListActivePlayer[1]
                            print("delete [1]")
                        if not tmpListActivePlayer[0] and tmpListActivePlayer[1]:
                            del ListActivePlayer[0]
                            print("delete[0]")
            iActivePlayer = 0
            #generate new tmpList
            tmpListActivePlayer.clear()
            for x in range(0, len(ListActivePlayer)):
                tmpListActivePlayer.append(False)
                print("neu generierte tmpListe: " + str(tmpListActivePlayer[x]))

        #final shooutout
        if len(ListActivePlayer) == 2:
            xFinalshootout = True
            print("final shootout")
        #winner
        if len(ListActivePlayer) == 1:
            xWin = True
            print("Win")

    def checkTargets():
        global jackfruit_done,stinkfrucht_done,ananas_done,sauersack_done,kiwi_done,birne_done,banane_done,apfel_done,orange_done,himbeere_done,kirsche_done,brombeere_done,erdbeere_done
        global jackfruit_hit,stinkfrucht_hit,ananas_hit,sauersack_hit,kiwi_hit,birne_hit,banane_hit,apfel_hit,orange_hit,himbeere_hit,kirsche_hit,brombeere_hit,erdbeere_hit
        global yJackFruit, ystinkfrucht, yananas, ysauersack, ykiwi, ybirne, ybanane, yapfel, yorange, yhimbeere, ykirsche, ybrombeere, yerdbeere
        global xResetFruits,iTmpCount

        if erdbeere_done:
            if brombeere_done:
                if kirsche_done:
                    if himbeere_done:
                        if orange_done:
                            if apfel_done:
                                if banane_done:
                                    if birne_done:
                                        if kiwi_done:
                                            if sauersack_done:
                                                if ananas_done:
                                                    if stinkfrucht_done:
                                                        if jackfruit_done:
                                                            iTmpCount += 1
                                                            if iTmpCount > 65:
                                                                xResetFruits = True
        if xResetFruits:
            erdbeere_done = False
            erdbeere_hit = False
            brombeere_done = False
            brombeere_hit = False
            kirsche_done = False
            kirsche_hit = False
            himbeere_done = False
            himbeere_hit = False
            orange_done = False
            orange_hit = False
            apfel_done = False
            apfel_hit = False
            banane_done = False
            banane_hit = False
            birne_done = False
            birne_hit = False
            kiwi_done = False
            kiwi_hit = False
            sauersack_done = False
            sauersack_hit = False
            ananas_done = False
            ananas_hit = False
            stinkfrucht_done = False
            stinkfrucht_hit = False
            jackfruit_done = False
            jackfruit_hit = False
            yJackFruit = 410
            ystinkfrucht = 470
            yananas = 430
            ysauersack = 410
            ykiwi = 310
            ybirne = 310
            ybanane = 250
            yapfel = 260
            yorange = 310
            yhimbeere = 150
            ykirsche = 150
            ybrombeere = 170
            yerdbeere = 160
            iTmpCount = 0
            xResetFruits = False


    def reset_parameter():
        global Diabolo_Rect,mausx,mausy
        Diabolo_Rect = [-20, -20]
        mausx = 0
        mausy = 0


    ###########define masks############
    mask_jackfruit = pygame.mask.from_surface(JackFruit)
    mask_stinkfrucht = pygame.mask.from_surface(Stinkfrucht)
    mask_ananas = pygame.mask.from_surface(Ananas)
    mask_sauersack = pygame.mask.from_surface(Sauersack)
    mask_kiwi = pygame.mask.from_surface(Kiwi)
    mask_birne = pygame.mask.from_surface(Birne)
    mask_bananen = pygame.mask.from_surface(Bananen)
    mask_apfel = pygame.mask.from_surface(Apfel)
    mask_orange = pygame.mask.from_surface(Orange)
    mask_himbeere = pygame.mask.from_surface(Himbeere)
    mask_kirsche = pygame.mask.from_surface(Kirsche)
    mask_Brombeere = pygame.mask.from_surface(Brombeere)
    mask_erdbeere = pygame.mask.from_surface(Erdbeere)
    mask_diabolo = pygame.mask.from_surface(Diabolo)

    # Start Game
    while hmsysteme.game_isactive():

        if xInitGame:
            # Create Playerclasses and tmpList
            for i in range(0, len(names)):
                Players.append(Player(names[i]))
                tmpListActivePlayer.append(False)
                ListActivePlayer.append(names[i])
                print("tmpListe: " + str(tmpListActivePlayer[i]))
                print("ActivePlayers: " + str(ListActivePlayer[i]))
            xInitGame = False

        for event in pygame.event.get():
            # Beenden bei [ESC] oder [X]
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                hit_for_screenshot = True
                mausx = event.pos[0]  # pos = pygame.mouse.get_pos() MAUSPOSITION ingame
                mausy = event.pos[1]
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
                screen.blit(Diabolo, Diabolo_Rect)

                Evaluation()

                # Screenshot
                if hit_for_screenshot:
                    screen.blit(Diabolo, Diabolo_Rect)
                    pygame.display.flip()
                    hmsysteme.take_screenshot(screen)
                    hit_for_screenshot = False


        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            mausx = pos[0]
            mausy = pos[1]
            Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
            screen.blit(Diabolo, Diabolo_Rect)

            Evaluation()

        # Screenshot
        if hit_for_screenshot:
            screen.blit(Diabolo, Diabolo_Rect)
            pygame.display.flip()
            hmsysteme.take_screenshot(screen)
            hit_for_screenshot = False

        #check if all fruits are done
        checkTargets()
        #Zeichnen
        zeichnen()

        if xCoulourStart:
            iColourCount += 1
            if iColourCount == 30:
                hmsysteme.put_rgbcolor((0, 0, 0))
                xCoulourStart = False
                iColourCount = 0

        clock.tick(framerate)

if __name__ == '__main__':
    main()


