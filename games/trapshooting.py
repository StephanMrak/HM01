def main():    
    import random
    import pygame   
    import math
    import time
    import hmsysteme
    import random
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE= (0, 191, 255)
    RED = (255, 0, 0)
    GREEN = (124, 252, 0)
    arrey = []
    anzahl = 3
    count=0
    countn=0
    last_hit = []
    last_hit.append(0)
    size = hmsysteme.get_size()
    pos = ([0, 0])
    names = hmsysteme.get_playernames()
    if not names:
        names = "dummy"
    points = []
    for i in range(0, len(names)):
        points.append(0)
    curr_player = 0

    class MyClass:   
        def __init__(self):
            self.hitormiss=False
            self.radius = 50
            self.dx=random.randint(1,4)
            self.dy=random.randint(-1,1)
            self.x = 0
            self.y = hmsysteme.get_size()[1] / 2
            self.num = 0
            self.rscale = 0
            self.lock = False
            self.width = 2
            self.color = WHITE

        def f(self):
            self.x += self.dx
            self.y += self.dy
            if self.x > hmsysteme.get_size()[0] or self.y >hmsysteme.get_size()[1] or self.y == 0:
                self.hitormiss=True
            pygame.draw.circle(screen, self.color, [int(self.x), int(self.y)], self.radius, self.width)


        def hit(self, fpos):
            if self.radius**2 >= ((fpos[0] - self.x) ** 2 + (fpos[1] - self.y) ** 2) >= (self.rscale * (self.num - 1))**2:
                last_hit[0] = 10000/self.radius
                points[curr_player] += last_hit[0]
                font = pygame.font.SysFont(pygame.font.get_fonts()[0], 28)
                text = font.render(str(str(int(last_hit[0]))), True, BLUE)
                screen.blit(text, (fpos[0] - text.get_width()+100 // 2, fpos[1] - text.get_height()+20 // 2))
                self.color = GREEN
                self.width=self.radius
                self.dx=0
                self.dy=0
                self.hitormiss=True
                #hmsysteme.put_rgbcolor([int(255- (last_hit[0]-5)*((255-0)/(250-5))),int((last_hit[0]-5)*((255-0)/(250-5))), 0])
                del font
                return True
            else:
                return False

    pygame.init()
    screen=pygame.display.set_mode(size, pygame.NOFRAME)
    pygame.display.set_caption("my game")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    for i in range(0, anzahl):
        arrey.append(MyClass())


    while hmsysteme.game_isactive():
        screen.fill(BLACK)
        for i in range(0, anzahl):
            arrey[i].f()
            count = count+arrey[i].hitormiss
            print(count)
        if count == anzahl:
            for i in range(0, anzahl):
                arrey[i].__init__()
        count=0

        font = pygame.font.SysFont(pygame.font.get_fonts()[0], 28)
        pygame.draw.circle(screen, BLUE, [50, 300 + (40 * (curr_player + 1))], 10, 10)
        for i in range(0, len(names)):
            text = font.render(str(names[i] + " " + str(int(points[i]))), True, BLUE)
            screen.blit(text, (200 - text.get_width() // 2, 300 + (40 * (i + 1)) - text.get_height() // 2))
        del font

        if hmsysteme.hit_detected():
            pos = hmsysteme.get_pos()

            for i in range(0, len(arrey)):
                for i in range(0, len(arrey)):
                    if arrey[i].hit(pos):
                        pass
                    else:
                        countn += 1
                if countn == len(arrey):
                    if curr_player == len(names) - 1:
                        curr_player = 0
                    else:
                        curr_player += 1
                    print("gepoppt")
                    print(i)
                countn = 0
                    #hmsysteme.put_rgbcolor(arrey[i].color)
            pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
            hmsysteme.take_screenshot(screen)

        for event in pygame.event.get():            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i in range(0, len(arrey)):
                    if arrey[i].hit(pos):
                        pass
                    else:
                        countn+=1
                if countn==len(arrey):
                    if curr_player == len(names)-1:
                        curr_player = 0
                    else:
                        curr_player += 1
                    print("gepoppt")
                    print(i)
                countn=0
                        #hmsysteme.put_rgbcolor(arrey[i].color)
                pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
                hmsysteme.take_screenshot(screen)
                

        pygame.display.flip()
        # print(clock.get_fps())
        clock.tick(60)
    pygame.display.quit()     
    pygame.quit()
    
    
if __name__ == '__main__':
    main()

                
                

