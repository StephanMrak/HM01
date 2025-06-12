def main():
    import pygame
    import random
    import time
    import math
    import time
    import hmsysteme
    import os
    import platform
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 191, 255)
    RED = (255, 0, 0)
    GREEN = (124, 252, 0)
    arrey = []
    anzahl = 10
    last_hit = []
    last_hit.append(0)
    size = hmsysteme.get_size()
    print(size)
    pos = ([0, 0])
    names = hmsysteme.get_playernames()
    hmsysteme.put_button_names(["reset"])
    WIDTH=50
    if not names:
        names = "dummy"
    points = []
    for i in range(0, len(names)):
        points.append(0)
    curr_player = 0


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


    class snake():
        def __init__(self):
            self.color=GREEN
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





    newsnake=snake()

    while hmsysteme.game_isactive():
        # print(os.environ["hm_GameIsActive"])
        screen.fill(BLACK)
        # font = pygame.font.SysFont(pygame.font.get_fonts()[0], 28)
        font = pygame.font.Font(None, 28)
        pygame.draw.circle(screen, BLUE, [50, 300 + (40 * (curr_player + 1))], 10, 10)
        for i in range(0, len(names)):
            text = font.render(str(names[i] + " " + str(int(points[i]))), True, BLUE)
            screen.blit(text, (200 - text.get_width() // 2, 300 + (40 * (i + 1)) - text.get_height() // 2))
        del font
        a = hmsysteme.get_action()
        newsnake.movesnake()
        newsnake.draw()
        if random.randrange(0,10)==5:
            newsnake.changedirection()






        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                    # hmsysteme.put_rgbcolor(arrey[i].color)
                mausx = event.pos[0]  # pos = pygame.mouse.get_pos() MAUSPOSITION ingame
                mausy = event.pos[1]
                Diabolo_Rect = pygame.Rect(mausx - 9, mausy - 9, 18, 18)
                newsnake.addblock()

                # pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
                hmsysteme.take_screenshot(screen)

        if hmsysteme.hit_detected():
            pos = hmsysteme.get_pos()
            pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
            hmsysteme.take_screenshot(screen)
            newsnake.addblock()

        screen.blit(Diabolo, Diabolo_Rect)
        pygame.display.flip()
        # print(clock.get_fps())
        clock.tick(2)

    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()




