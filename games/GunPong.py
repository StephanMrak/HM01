
def main():
    global mausx,mausy,hit_for_screenshot
    global xBall,yBall,offsetBall,xBall_hit,xBall_blocked,xPositiv,xNegativ,xCountRounds,ixBallSpeed,xFault,ixBallSpeedtmp
    global iPlayerPointsLeft,iPlayerPointsRight,listYspeed,iyBallSpeed,xYNegieren
    global xPlayerLeft,xPlayerRight,xNewRound,xNewRoundreal,iCountNextRound,xCountNextRound,iPointsMax,xGameOver,xActivePlayer,iGetAction
    global xGo,Diabolo_Rect
    import pygame
    import time
    import hmsysteme
    import os
    import platform
    import random
    import pygame.freetype
    hmsysteme.put_button_names(["ENTER", "RESTART", "x", "x", "x", "x", "x", "x", "x"])
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
        path = path.replace('GunPong.py', '')
    else:
        path = path.replace('GunPong.py', '')

    #screen = pygame.display.set_mode(size)
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    clock = pygame.time.Clock()
    pygame.display.set_caption("ePong")

    #Pics
    Diabolo = pygame.image.load(os.path.join(path, "pics/GunPong/Schuss.png"))
    pic_Field = pygame.image.load(os.path.join(path, "pics/GunPong/Fieldx.png"))
    pic_Ball = [pygame.image.load(os.path.join(path, "pics/GunPong/Ball.png")), pygame.image.load(os.path.join(path, "pics/GunPong/Ballx.png")),
                pygame.image.load(os.path.join(path, "pics/GunPong/Ballxx.png"))]

    #TextFonds
    TXT_ROUNDS = pygame.font.SysFont("Times", 40)
    TXT_FAULT = pygame.font.SysFont("Times", 150)

    ############Variablen###########
    HIMMELBLAU = (120, 210, 255)
    FIREARMS = (70, 70, 70)
    framerate = 30
    mausx = 0
    mausy = 0
    hit_for_screenshot = False
    xBall = 400
    yBall = 200
    offsetBall = 0
    xBall_hit = False
    offsetDiabolo = 9
    xBall_blocked = False
    xPositiv = True
    xNegativ = False
    xCountRounds = 0
    ixBallSpeed = 1
    xFault = False
    iPlayerPointsLeft = 0
    iPlayerPointsRight = 0
    xPlayerLeft = False
    xPlayerRight = False
    xNewRound = False
    listYspeed = (0, 1, 2, 3, 4)
    iyBallSpeed = 0
    xYNegieren = False
    xNewRoundreal = False
    iCountNextRound = 91
    xCountNextRound = True
    iPointsMax = 10
    xGameOver = False
    xActivePlayer = True #left = True, rigt = False
    iGetAction = 0
    xGo = False
    Diabolo_Rect = (0,0)
    ixBallSpeedtmp = 0

    class Player():
        def __init__(self, name, score):
            self.name = name
            self.score = score

    def zeichnen():
        global xBall,yBall,xBall_blocked,xBall_hit,xPositiv,xNegativ,xCountRounds,ixBallSpeed,iyBallSpeed
        global xPlayerRight,xPlayerLeft,iPlayerPointsLeft,iPlayerPointsRight,listYspeed,xYNegieren
        global xNewRoundreal,xNewRound,iCountNextRound,xCountNextRound,iPointsMax,xGameOver,xActivePlayer,xGo
        global ixBallSpeedtmp

        if xPlayerLeft and not xCountNextRound:
            iPlayerPointsLeft += 1
            xCountNextRound = True
        if xPlayerRight and not xCountNextRound:
            iPlayerPointsRight += 1
            xCountNextRound = True
        if iPlayerPointsRight == iPointsMax:
            xGameOver = True
        if  iPlayerPointsLeft == iPointsMax:
            xGameOver = True

        if not xGameOver:
            if xCountNextRound:#prepare for next round
                if xGo:
                    iCountNextRound -= 1
                screen.fill(FIREARMS)
                screen.blit(pic_Field, (0, 0))
                txtRounds = TXT_ROUNDS.render("Rally: " + str(xCountRounds), True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), [600, 41, 165, 45], 0)
                screen.blit(txtRounds, (610, 40))
                txtPlayer1 = TXT_ROUNDS.render("Points: " + str(iPlayerPointsLeft), True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), [106, 41, 170, 45], 0)
                screen.blit(txtPlayer1, (115, 40))
                txtPlayer2 = TXT_ROUNDS.render("Points: " + str(iPlayerPointsRight), True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), [1089, 41, 170, 45], 0)
                screen.blit(txtPlayer2, (1100, 40))
                if iCountNextRound > 90:
                    txtCountdown = TXT_ROUNDS.render("Press ENTER", True, (0, 0, 0))
                    pygame.draw.rect(screen, (255, 255, 255), [550, 93, 280, 50], 0)
                    screen.blit(txtCountdown, (580, 93))
                if iCountNextRound > 60 and iCountNextRound < 90:
                    txtCountdown = TXT_FAULT.render("2", True, (0, 0, 0))
                    pygame.draw.rect(screen, (255, 255, 255), [540, 110, 290, 150], 0)
                    screen.blit(txtCountdown, (645, 100))
                if iCountNextRound < 60 and iCountNextRound > 30:
                    txtCountdown = TXT_FAULT.render("1", True, (0, 0, 0))
                    pygame.draw.rect(screen, (255, 255, 255), [540, 110, 290, 150], 0)
                    screen.blit(txtCountdown, (645, 100))
                if iCountNextRound < 30 and iCountNextRound >= 0:
                    txtCountdown = TXT_FAULT.render("GO!", True, (0, 0, 0))
                    pygame.draw.rect(screen, (255, 255, 255), [540, 110, 290, 150], 0)
                    screen.blit(txtCountdown, (550, 100))
                pygame.display.flip()
                if iCountNextRound <= 0:
                    if xPlayerLeft:
                        xBall = 400
                        xPositiv = True
                        xActivePlayer = True
                    if xPlayerRight:
                        xBall = 766
                        xPositiv = False
                        xActivePlayer = False
                    ixBallSpeed = 1
                    iCountNextRound = 91
                    xCountRounds = 0
                    xGo = False
                    xPlayerLeft = False
                    xPlayerRight = False
                    xCountNextRound = False

            else:#actual gameplay
                if xYNegieren:
                    yBall += iyBallSpeed
                else:
                    yBall -= iyBallSpeed

                if xPositiv:
                    xBall += ixBallSpeed
                else:
                    xBall -= ixBallSpeed
                # Calculate the Balls direction
                if xBall_hit and xPositiv:
                    xActivePlayer = False
                    xCountRounds += 1
                    ixBallSpeedtmp += 1
                    if ixBallSpeedtmp == 2:
                        ixBallSpeed += 1
                        ixBallSpeedtmp = 0
                    xPositiv = False
                    xBall_hit = False
                elif xBall_hit and not xPositiv:
                    xActivePlayer = True
                    ixBallSpeed += 1
                    xCountRounds += 1
                    xPositiv = True
                    xBall_hit = False
                # Print Scoreboards and field
                screen.fill(FIREARMS)
                screen.blit(pic_Field, (0, 0))
                if xBall_blocked:
                    screen.blit(pic_Ball[1], (xBall, yBall))
                else:
                    screen.blit(pic_Ball[0], (xBall, yBall))
                txtRounds = TXT_ROUNDS.render("Rally: " + str(xCountRounds), True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), [600, 41, 165, 45], 0)
                screen.blit(txtRounds, (610, 40))
                txtPlayer1 = TXT_ROUNDS.render("Points: " + str(iPlayerPointsLeft), True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), [106, 41, 170, 45], 0)
                screen.blit(txtPlayer1, (115, 40))
                txtPlayer2 = TXT_ROUNDS.render("Points: " + str(iPlayerPointsRight), True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), [1089, 41, 170, 45], 0)
                screen.blit(txtPlayer2, (1100, 40))
                pygame.display.flip()

        if xGameOver:
            screen.fill(FIREARMS)
            screen.blit(pic_Field, (0, 0))
            txtPlayer1 = TXT_FAULT.render(str(iPlayerPointsLeft), True, (0, 0, 0))
            screen.blit(txtPlayer1, (300, 300))
            txtPlayer2 = TXT_FAULT.render(str(iPlayerPointsRight), True, (0, 0, 0))
            screen.blit(txtPlayer2, (1000, 300))
            txtRestart = TXT_ROUNDS.render("Press RESTART Button for next Round!", True, (0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), [360, 145, 670, 50], 0)
            screen.blit(txtRestart, (370, 150))
            pygame.display.flip()



    def reset_parameter():
        global Diabolo_Rect,mausx,mausy
        Diabolo_Rect = [-20, -20]
        mausx = 0
        mausy = 0

    def ButtonHandler():
        global iGetAction,xGo,xGameOver,xBall,yBall,xCountRounds,ixBallSpeed,xPositiv,iCountNextRound
        global iPlayerPointsLeft,iPlayerPointsRight
        iGetAction = hmsysteme.get_action()
        if iGetAction > 0:
            # Enter
            if iGetAction == 1:
                xGo = True
            # Restart
            if iGetAction == 2:
                xGameOver = False
                xBall = 400
                yBall = 200
                xCountRounds = 0
                ixBallSpeed = 1
                xPositiv = True
                iCountNextRound = 91
                iPlayerPointsLeft = 0
                iPlayerPointsRight = 0

    ###########define masks############
    MaskDiabolo = pygame.mask.from_surface(Diabolo)
    mask_Ball = pygame.mask.from_surface(pic_Ball[0])
    #pygame.mouse.set_visible(False)
    # Start Game
    while hmsysteme.game_isactive():

        ButtonHandler()
        iGetAction = 0
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
                print("X: ", mausx, "Y: ", mausy)
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
                screen.blit(Diabolo, Diabolo_Rect)

                # Screenshot
                if hit_for_screenshot:
                    screen.blit(Diabolo, Diabolo_Rect)
                    pygame.display.flip()
                    hmsysteme.take_screenshot(screen)
                    hit_for_screenshot = False

                offsetBall = (int(mausx - (xBall + offsetDiabolo)), int(mausy - (yBall + offsetDiabolo)))
                if mask_Ball.overlap(MaskDiabolo, offsetBall) and not xBall_blocked:
                    xBall_hit = True
                    iyBallSpeed = random.choice(listYspeed)
                    reset_parameter()

        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            mausx = pos[0]
            mausy = pos[1]
            Diabolo_Rect = pygame.Rect(pos[0] - 9, pos[1] - 9, 18, 18)
            screen.blit(Diabolo, Diabolo_Rect)

            offsetBall = (int(mausx - (xBall + offsetDiabolo)), int(mausy - (yBall + offsetDiabolo)))
            if mask_Ball.overlap(MaskDiabolo, offsetBall) and not xBall_blocked:
                xBall_hit = True
                iyBallSpeed = random.choice(listYspeed)
                reset_parameter()

        xBall_blocked = False
        if xBall <  533 and xActivePlayer:
            xBall_blocked = True
        if xBall > 683 and not xActivePlayer:
            xBall_blocked = True

        if yBall < 93:
            xYNegieren = True
        if yBall > 533:
            xYNegieren = False
        if xBall < 113 + ixBallSpeed and not xCountNextRound:
            xPlayerRight = True
            hit_for_screenshot = True
        if xBall > 1102 - ixBallSpeed and not xCountNextRound:
            xPlayerLeft = True
            hit_for_screenshot = True

        # Screenshot
        if hit_for_screenshot:
            screen.blit(Diabolo, Diabolo_Rect)
            pygame.display.flip()
            hmsysteme.take_screenshot(screen)
            hit_for_screenshot = False
        #Zeichnen
        zeichnen()
        clock.tick(framerate)

if __name__ == '__main__':
    main()


