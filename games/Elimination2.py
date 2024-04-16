def main(): 
    import time
    import pygame
    import math
    import random
    import os
    import sys
    from itertools import cycle
    import hmsysteme

    #Globale Einstellungen
    gBLINKDELAY = 370 #milliseconds
    gFPS = 60
    gBLINKCOUNTER = 5
    size = hmsysteme.get_size()
    path=os.path.realpath(__file__)
    path=path.replace('games/Elimination2.py', '')
    #path = r"C:/Users/flori/Dropbox/Telespiel/Raspi_Programme/HM01_v0.1/"
    print(__file__)
    # some colors to use
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 191, 255)
    RED = (255, 0, 0)
    HIMMELBLAU = (120, 210, 255)
    YELLOW = (255,255,0)

    #Pygame init
    clock = pygame.time.Clock()
    pygame.display.set_caption("Shooting")

    mausx = 0
    mausy = 0
    arrblinkdone = [False,False,False,False]
    blinkdone = False
    carryOn = False
    hit = False
    x_1 = 0
    y_1 = 0
    TrefferKopf = False
    blinkenKopfdone = False
    TrefferRumpf = False
    blinkenRumpfdone = False
    TrefferArm = False
    blinkenArmdone = False
    TrefferBeine = False
    blinkenBeinedone = False
    aktivePlayer = 0
    aktiveSpieler = []
    #Zeit
    BLINK_EVENT = pygame.USEREVENT
    my_clock = pygame.time.Clock()
    BLINKTAKT = False
    hitmouse = False
    sWin = ""
    ResetGame = False
    iWait = 0
    homerlist = []
    final = False
    final_hit = False

    #Bilder initialisieren
    Homer = [pygame.image.load(os.path.join(path,"games/pics/Homer_Kopf.png")),pygame.image.load(os.path.join(path,"games/pics/Homer_Arm.png")),
             pygame.image.load(os.path.join(path,"games/pics/Homer_Beine.png")),pygame.image.load(os.path.join(path,"games/pics/Homer_Rumpf.png"))]
    hintergrund = pygame.image.load(os.path.join(path,"games/pics/hintergrund_hm01.png"))

    #Init Hitbox Kopf


    def zeichnen(x,y):
        screen.blit(hintergrund, (0, 0))
        if TrefferKopf:
            arrblinkdone[0] = blinken(Homer[0],572,118,blinkenKopf)
        else:
            screen.blit(Homer[0],(572,118))
        if TrefferArm:
            arrblinkdone[1] = blinken(Homer[1],484,231,blinkenArm)
        else:
            screen.blit(Homer[1],(484,231))
        if TrefferBeine:
            arrblinkdone[2] = blinken(Homer[2],530,432,blinkenBeine)
        else:
            screen.blit(Homer[2],(530,432))
        if TrefferRumpf:
            arrblinkdone[3] = blinken(Homer[3],531,283,blinkenRumpf)
        else:
            screen.blit(Homer[3],(531,283))
        #pygame.draw.circle(screen,RED,[x,y],8,4)
        #pygame.draw.rect(screen,YELLOW,Diabolo_Rect)
        screen.blit(Diabolo,Diabolo_Rect)
        pygame.display.flip()

    def blinken(bild,x,y,counter):
        blinktest = False
        if BLINKTAKT:
            if counter < gBLINKCOUNTER * 2:
                screen.blit(bild, (x,y))
                blinktest = False
            else:
                blinktest = True
        return blinktest

    #Init Shooting
    homerlist = []
    kopf_mask = pygame.mask.from_surface(Homer[0])
    rumpf_mask = pygame.mask.from_surface(Homer[3])
    arm_mask = pygame.mask.from_surface(Homer[1])
    bein_mask = pygame.mask.from_surface(Homer[2])
    #homerlist.append(kopf_mask)
    for pic in Homer:
        homerlist.append(pygame.mask.from_surface(pic))

    Diabolo = pygame.image.load(os.path.join(path,"games/pics/Schuss.png"))
    Diabolo_Mask = pygame.mask.from_surface(Diabolo)
    Diabolo_Rect = Diabolo.get_rect(center=(50,50))

    NullSchuss = pygame.Rect(0,0,1,1)
    Schuss = pygame.Rect(0,0,15,15)
    carryOn = True
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(size, pygame.NOFRAME)
    #pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()


    blinkenKopf = 0
    blinkenRumpf = 0
    blinkenArm = 0
    blinkenBeine = 0
    def ShotEvaluation(aPlayer):
        if len(Namenliste) > 1:
            if aPlayer == len(Namenliste) - 1:
                Namenliste.pop(aPlayer)
                print("nicht getroffen und setze Spieler auf 0")
                player = 0
                return player
            else:
                Namenliste.pop(aPlayer)
        if len(Namenliste) == 1:
            ResetGame = True

    #Zeit Ereignisse
    pygame.time.set_timer(BLINK_EVENT, gBLINKDELAY)

    class Spieler:
        Anzahl = 0 
        def __init__(self,name):
            self.name = name
            Spieler.Anzahl += 1
            print("spieler erstellt")
        def kill(self):
            Spieler.Anzahl -= 1

 #   my_Players = []
    Namenliste = hmsysteme.get_playernames()
 #   for i in range(0,len(Namenliste)):
 #       my_Players.append(Spieler(Namenliste[i]))


    while carryOn and hmsysteme.game_isactive():
        
        screen.fill(HIMMELBLAU)

        #print something to the pygame window
        font = pygame.font.SysFont(pygame.font.get_fonts()[0], 50)
        
        if ResetGame:
            if iWait < 200:
                iWait += 1
                sWinner = str(Namenliste[aktivePlayer]) + " Wins!!!"
                font = pygame.font.SysFont(pygame.font.get_fonts()[0], 80)
                text = font.render((str(sWinner)), True, (239, 116, 33))
            else:
                Namenliste = hmsysteme.get_playernames()
                ResetGame = False
                aktivePlayer = 0
                iWait = 0
                blinkenKopf = 0
                blinkenRumpf = 0
                blinkenArm = 0
                blinkenBeine = 0
                TrefferKopf = False
                TrefferRumpf = False
                TrefferArm = False
                TrefferBeine = False
                arrblinkdone[0] = False
                arrblinkdone[1] = False
                arrblinkdone[2] = False
                arrblinkdone[3] = False
        else:
            text = font.render(str(Namenliste[aktivePlayer]), True, (200, 100, 50))
        screen.blit(text,(320 - text.get_width() // 2, 240 - text.get_height() // 2))
        #delete created font to avoid pygame bug
        del font


        if hmsysteme.hit_detected():
            x_1,y_1 = hmsysteme.get_pos()
            Diabolo_Rect = pygame.Rect(x_1-5,y_1-5,10,10)
            hit = True

        #create your game here
        for event in pygame.event.get():
            if event.type == BLINK_EVENT or hit:
                BLINKTAKT = not BLINKTAKT
                if TrefferKopf and not blinkenKopfdone:
                    blinkenKopf += 1
                if TrefferArm and not blinkenArmdone:
                    blinkenArm += 1
                if TrefferRumpf and not blinkenRumpfdone:
                    blinkenRumpf += 1
                if TrefferBeine and not blinkenBeinedone:
                    blinkenBeine += 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                mausx = event.pos[0]    #pos = pygame.mouse.get_pos() mausposition ingame
                mausy = event.pos[1]
                print("x:", mausx, "y:", mausy)
                Diabolo_Rect = pygame.Rect(mausx-5,mausy-5,10,10)
                hitmouse = True
                hit = True
                
        #all_sprites.update()
        #.....
        if hitmouse:
            zeichnen(mausx,mausy)
            hitmouse = False
        else:
            zeichnen(x_1,y_1)
        #check if the screen has been hit by a bullet
            
        if hit == True:
            Schuss = pygame.Rect(x_1 - 8,y_1 - 8,15,15)
            offsetRumpf = (mausx - 536,mausy - 288)
            offsetArm = (mausx - 489,mausy - 236)
            offsetKopf = (mausx - 577,mausy - 123)
            offsetBeine = (mausx - 535,mausy-437)
            
            if kopf_mask.overlap(Diabolo_Mask,offsetKopf) and hit: 
                hit = False
                print("Kopf")
                if not TrefferKopf:
                    if aktivePlayer < len(Namenliste) - 1:
                        aktivePlayer += 1
                    else:
                        aktivePlayer = 0
                    TrefferKopf = True
                    final_hit = True
                else:
                    final_hit = False
                    if len(Namenliste) > 1:
                        if aktivePlayer == len(Namenliste) - 1:
                            Namenliste.pop(aktivePlayer)
                            print("nicht getroffen und setze Spieler auf 0")
                            aktivePlayer = 0
                        else:
                            Namenliste.pop(aktivePlayer)
                if len(Namenliste) == 1:
                    ResetGame = True

            if rumpf_mask.overlap(Diabolo_Mask,offsetRumpf) and hit:
                hit = False
                print("Rumpf")
                if not TrefferRumpf:
                    if aktivePlayer < len(Namenliste) - 1:
                        aktivePlayer += 1
                    else:
                        aktivePlayer = 0
                    TrefferRumpf = True
                    final_hit = True
                else:
                    final_hit = False
                    if len(Namenliste) > 1:
                        if aktivePlayer == len(Namenliste) - 1:
                            Namenliste.pop(aktivePlayer)
                            print("nicht getroffen und setze Spieler auf 0")
                            aktivePlayer = 0
                        else:
                            Namenliste.pop(aktivePlayer)
                    if len(Namenliste) == 1:
                        ResetGame = True

            if arm_mask.overlap(Diabolo_Mask,offsetArm) and hit:
                hit = False
                print("Arm")
                if not TrefferArm:
                    if aktivePlayer < len(Namenliste) - 1:
                        aktivePlayer += 1
                    else:
                        aktivePlayer = 0
                    TrefferArm = True
                    final_hit = True
                else:
                    final_hit = False
                    if len(Namenliste) > 1:
                        if aktivePlayer == len(Namenliste) - 1:
                            Namenliste.pop(aktivePlayer)
                            print("nicht getroffen und setze Spieler auf 0")
                            aktivePlayer = 0
                        else:
                            Namenliste.pop(aktivePlayer)
                    if len(Namenliste) == 1:
                        ResetGame = True

            if bein_mask.overlap(Diabolo_Mask,offsetBeine) and hit:
                hit = False
                print("Beine")
                if not TrefferBeine:
                    if aktivePlayer < len(Namenliste) - 1:
                        aktivePlayer += 1
                    else:
                        aktivePlayer = 0
                    TrefferBeine = True
                    final_hit = True
                else:
                    final_hit = False
                    if len(Namenliste) > 1:
                        if aktivePlayer == len(Namenliste) - 1:
                            Namenliste.pop(aktivePlayer)
                            print("nicht getroffen und setze Spieler auf 0")
                            aktivePlayer = 0
                        else:
                            Namenliste.pop(aktivePlayer)
                    if len(Namenliste) == 1:
                        ResetGame = True

            if not bein_mask.overlap(Diabolo_Mask,offsetBeine) and not arm_mask.overlap(Diabolo_Mask,offsetArm) and not rumpf_mask.overlap(Diabolo_Mask,offsetRumpf) and not kopf_mask.overlap(Diabolo_Mask,offsetKopf) and hit:
                final_hit = False
                hit = False
                if len(Namenliste) > 1:
                    if aktivePlayer == len(Namenliste) - 1:
                        Namenliste.pop(aktivePlayer)
                        print("nicht getroffen und setze Spieler auf 0")
                        aktivePlayer = 0
                    else:
                        Namenliste.pop(aktivePlayer)

                if len(Namenliste) == 1:
                    ResetGame = True

            if len(Namenliste) == 2:
                final = True

            print("Finaler Hit:",final_hit)
            print("Groeße Namenliste:", len(Namenliste))       
            print("finale:",final)
            
            #safe screenshot of bullet location
            hmsysteme.take_screenshot(screen)
#                os.remove(os.path.join(path,"screencapture.png"))
#                pygame.image.save(screen, os.path.join(path,"screencapture.png"))

        if (TrefferKopf and TrefferRumpf and TrefferArm and TrefferBeine and arrblinkdone[0] and arrblinkdone[1] and arrblinkdone[2] and arrblinkdone[3]):
            blinkenKopf = 0
            blinkenRumpf = 0
            blinkenArm = 0
            blinkenBeine = 0
            TrefferKopf = False
            TrefferRumpf = False
            TrefferArm = False
            TrefferBeine = False
            arrblinkdone[0] = False
            arrblinkdone[1] = False
            arrblinkdone[2] = False
            arrblinkdone[3] = False
            
        clock.tick(gFPS)
        #close pygame window
    pygame.font.quit()
    pygame.display.quit()    
    pygame.quit() 

if __name__ == '__main__':
    main()