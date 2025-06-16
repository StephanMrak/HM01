def main():
    import pygame
    import random
    import hmsysteme
    import os
    import platform
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 191, 255)
    RED = (255, 0, 0)
    GREEN = (124, 252, 0)
    colors=[]
    colors.append(WHITE)
    colors.append(BLUE)
    colors.append(RED)
    colors.append(GREEN)

    last_hit = []
    last_hit.append(0)
    size = hmsysteme.get_size()
    snakes=[]
    names = hmsysteme.get_playernames()
    hmsysteme.put_button_names(["set time:60sek", "set time:120sek","set time:180sek","set time:300sek","set time:600sek", "add snake", "remove snake"])
    WIDTH=50
    POINTS=0
    TIME=60
    if not names:
        names = "dummy"
    points = []
    for i in range(0, len(names)):
        points.append(0)
    tick=2


    pygame.init()
    screen = pygame.display.set_mode(size)
    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("my game")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()


    path = os.path.realpath(__file__)
    print(path)

    if 'Linux' in platform.uname():
        path = path.replace('sneek.py', '')
    else:
        path = path.replace('sneek.py', '')

    # define masks
    Diabolo = pygame.image.load(os.path.join(path, "pics/Schuss.png"))
    Diabolo_Mask = pygame.mask.from_surface(Diabolo)
    Diabolo_Rect = Diabolo.get_rect()

    class Block():
        def __init__(self, pos, number):
            self.pos=pos
            self.number=number
            self.width=WIDTH

        def getrect(self):
            return [(self.pos[0],self.pos[1]),(self.pos[0],self.pos[1]+self.width),(self.pos[0]+self.width,self.pos[1]+self.width),(self.pos[0]+self.width,self.pos[1])]

        def checkifhit(self,hitcoords):
            if hitcoords[0]>self.pos[0]and hitcoords[0]<(self.pos[0]+self.width):
                if hitcoords[1] > self.pos[1] and hitcoords[1] < (self.pos[1] + self.width):
                    return True
                else:
                    return False
            else:
                return False



    class Snake():
        def __init__(self):
            self.color=random.choice(colors)
            self.speed=1
            self.direction=[1,0]
            self.blocks=[]
            self.width=WIDTH
            self.length=3
            self.blocks.append(Block([300,300],0))
            self.blocks.append(Block([300, 300+self.width], 1))
            self.blocks.append(Block([300, 300 + 2*self.width], 2))

        def addblock(self):
            for lastblock in self.blocks:
                if lastblock.number == self.length - 1:
                    self.length = self.length + 1
                    newblock=Block(lastblock.pos,number=self.length-1)
            self.blocks.append(newblock)


        def changedirection(self):
            self.direction=[random.randrange(-1,2),random.randrange(-1,2)]

        def movesnake(self):
            for lastblock in self.blocks:
                if lastblock.number==self.length-1:
                    for firstblock in self.blocks:
                        if firstblock.number==0:
                            safe_x=firstblock.pos[0]+self.direction[0]*self.width
                            safe_y=firstblock.pos[1]+self.direction[1]*self.width
                            if safe_x>size[0]:
                                safe_x=0
                            elif safe_x<0:
                                safe_x=size[0]
                            elif safe_y>size[1]:
                                safe_y=0
                            elif safe_y<0:
                                safe_y=size[1]

                            lastblock.pos=[safe_x,safe_y]
                            for block in self.blocks:
                                if block.number==self.length-1:
                                    block.number=0
                                else:
                                    block.number=block.number+1


                            return
        def draw(self):
            for block in self.blocks:
                pygame.draw.polygon(screen, self.color, block.getrect())




    snakes.append(Snake())
    gameover=False

    while hmsysteme.game_isactive():
        # print(os.environ["hm_GameIsActive"])
        screen.fill(BLACK)

        a= hmsysteme.get_action()
        if a==1:
            TIME=60
            POINTS=0
            for snake in snakes:
                snake.__init__()
            gameover = False
        elif a==2:
            TIME=120
            POINTS=0
            for snake in snakes:
                snake.__init__()
            gameover = False
        elif a == 3:
            TIME = 180
            POINTS = 0
            for snake in snakes:
                snake.__init__()
            gameover = False
        elif a == 4:
            TIME = 300
            POINTS = 0
            for snake in snakes:
                snake.__init__()
            gameover = False
        elif a == 5:
            TIME = 600
            POINTS = 0
            for snake in snakes:
                snake.__init__()
            gameover = False
        elif a == 6:
            snakes.append(Snake())
        elif a == 7:
            if len(snakes)>1:
                snakes.pop(-1)



        font = pygame.font.Font(None, 35)
        text = font.render(f"Time remaining: {round(TIME,1)}", True, BLUE)
        screen.blit(text, (100 , 200 ))

        if TIME <=0:
            TIME=0
            font2 = pygame.font.Font(None, 100)
            gameovertext = font2.render("Game Over!", True, (255, 0, 0))
            screen.blit(gameovertext, (500, 250))
            gameover=True
        TIME = TIME - (1 / tick)
        text = font.render(f"Points: {POINTS}", True, BLUE)
        screen.blit(text, (100 ,250))
        del font
        for snake in snakes:
            snake.movesnake()
            snake.draw()
            if random.randrange(0,10)==5:
                snake.changedirection()







        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and not gameover:
                pos = event.pos

                    # hmsysteme.put_rgbcolor(arrey[i].color)
                mausx = event.pos[0]  # pos = pygame.mouse.get_pos() MAUSPOSITION ingame
                mausy = event.pos[1]
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
                screen.blit(Diabolo, Diabolo_Rect)
                pygame.display.flip()
                for snake in snakes:
                    for block in snake.blocks:
                        if block.checkifhit([mausx,mausy])==True:
                            snake.addblock()
                            POINTS+=1
                            break


                # pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
                hmsysteme.take_screenshot(screen)

        if hmsysteme.hit_detected():
            pos = hmsysteme.get_pos()
            if not gameover:
                for snake in snakes:
                    for block in snake.blocks:
                        if block.checkifhit([pos[0], pos[1]]) == True:
                            snake.addblock()
                            POINTS += 1
                            break
            Diabolo_Rect = pygame.Rect(int(pos[0]) - 9, int(pos[1]) - 9, 18, 18)
            screen.blit(Diabolo, Diabolo_Rect)
            pygame.display.flip()
            hmsysteme.take_screenshot(screen)

        screen.blit(Diabolo, Diabolo_Rect)
        pygame.display.flip()
        # print(clock.get_fps())
        clock.tick(tick)

    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()




