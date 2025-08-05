def main():    
    import random
    import pygame   

    import hmsysteme
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE= (0, 191, 255)
    RED = (255, 0, 0)
    GREEN = (124, 252, 0)
    rings = []
    num_of_rings = 10
    last_hit = []
    last_hit.append(0)
    size = hmsysteme.get_size()
    print(size)
    names = hmsysteme.get_playernames()
    if not names:
        names = "dummy"
    points = []
    for i in range(0, len(names)):
        points.append(0)
    curr_player = 0

    class Ring():
        def __init__(self):
            self.radius = random.randint(70, 100)
            self.x = hmsysteme.get_size()[0]/2
            self.y = hmsysteme.get_size()[1] / 2
            self.num = 0
            self.rscale = 0
            self.lock = False
            self.destruct = False
            self.width = 5
            self.count = 0
            self.color = WHITE

        def f(self):
            if self.destruct:
                self.count += 1
                self.width = self.rscale
                if self.count > 20:
                    self.color = WHITE
                    self.count = 0
                    self.width = 5
                    self.destruct = False

            pygame.draw.circle(screen, self.color, [int(self.x), int(self.y)], self.radius + self.count, self.width
                               + 1 * self.count)

        def hit(self, fpos):
            if self.radius**2 >= ((fpos[0] - self.x) ** 2 + (fpos[1] - self.y) ** 2) >= (self.rscale * (self.num - 1))**2:
                self.color = (255 / num_of_rings * self.num, 255 - (255 * self.num / num_of_rings), 0)
                self.destruct = True
                last_hit[0] = 100 - ((self.num - 1) * (100 / num_of_rings))
                points[curr_player] += last_hit[0]
                font = pygame.font.Font(None, 28)
                text = font.render(str("last hit : " + str(int(last_hit[0]))), True, BLUE)
                screen.blit(text, (150 - text.get_width() // 2, 240 - text.get_height() // 2))
                del font
                return True                
            else:
                return False

    pygame.init()
    if hmsysteme.get_debug() == True:
        screen = pygame.display.set_mode(size)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("my game")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    for i in range(0, num_of_rings):
        rings.append(Ring())
        rings[i].rscale = 25
        rings[i].radius = (i + 1) * rings[i].rscale
        rings[i].num = i + 1
    while hmsysteme.game_isactive():
        while hmsysteme.get_busy():
            pass
        screen.fill(BLACK)

        for i in range(0, num_of_rings):
            rings[i].f()
        font = pygame.font.Font(None, 28)

        pygame.draw.circle(screen, BLUE, [50, 300 + (40 * (curr_player + 1))], 10, 10)
        for i in range(0, len(names)):
            text = font.render(str(names[i] + " " + str(int(points[i]))), True, BLUE)
            screen.blit(text, (200 - text.get_width() // 2, 300 + (40 * (i + 1)) - text.get_height() // 2))
        del font

        if hmsysteme.hit_detected():
            pos = hmsysteme.get_pos()

            for i in range(0, len(rings)):
                if rings[i].hit(pos):
                    if curr_player == len(names)-1:
                        curr_player = 0
                    else:
                        curr_player += 1
            pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
            hmsysteme.take_screenshot(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i in range(0, len(rings)):
                    if rings[i].hit(pos):
                        if curr_player == len(names)-1:
                            curr_player = 0
                        else:
                            curr_player += 1
                pygame.draw.circle(screen, RED, [int(pos[0]), int(pos[1])], int(3 / 0.3), 5)
                hmsysteme.take_screenshot(screen)
                

        pygame.display.flip()
        # print(clock.get_fps())
        clock.tick(60)
    pygame.display.quit()     
    pygame.quit()
    
    
if __name__ == '__main__':
    main()

                
                

