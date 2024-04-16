def main():    
    import random
    import pygame   
    import math
    import time
    import hmsysteme
    WHITE = ( 255, 255, 255)
    BLACK = ( 0, 0, 0)
    BLUE= (0,191,255)
    RED = ( 255, 0, 0)
    arrey=[]
    paare=[]
    anzahl=10
    size=hmsysteme.get_size()
    pos=([0,0])

    class MyClass:   
        def __init__(self):
            self.radius=random.randint(70, 100)
            self.x = random.randint(100, 800)
            self.y = random.randint(100, 400)
            self.lock=False
            self.destruct=False
            self.dir_vec = [random.randint(1,3),random.randint(1,3)]
            self.Farbe=(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        def f(self):
            if self.destruct:
                self.dir_vec = [0, 0]
                self.radius=self.radius+1
                if self.radius > 200:
                    self.x += size[0]
                    self.y += size[1]
                    self.radius = 1
                    self.destruct = False
            else:
                self.x=self.x+self.dir_vec[0]
                self.y=self.y+self.dir_vec[1]
            pygame.draw.circle(screen, self.Farbe, [int(self.x), int(self.y)], self.radius, self.radius)

        def hit(self,pos):
            if ((pos[0]-self.x)**2+(pos[1]-self.y)**2) <= self.radius**2:
                self.destruct=True
                return True                
            else:
                return False
        def x_neg(self):
            self.dir_vec[0]=-self.dir_vec[0]
        def y_neg(self):
            self.dir_vec[1]=-self.dir_vec[1]
    pygame.init()
    screen=pygame.display.set_mode(size, pygame.NOFRAME)
    pygame.display.set_caption("my game")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    for i in range(0,anzahl):
        arrey.append(MyClass())
        #arrey[i].x=(i+1)*150
    #x=MyClass()
   
    while hmsysteme.game_isactive():
        screen.fill(BLACK)
        for i in range(0,len(arrey)):
            arrey[i].f()
            if arrey[i].x>size[0]-arrey[i].radius:
                arrey[i].dir_vec[0]=-math.sqrt(arrey[i].dir_vec[0]**2)
            if arrey[i].x<=0+arrey[i].radius:
                arrey[i].dir_vec[0]=math.sqrt(arrey[i].dir_vec[0]**2)           
            if arrey[i].y>size[1]-arrey[i].radius:
                arrey[i].dir_vec[1]=-math.sqrt(arrey[i].dir_vec[1]**2)
            if arrey[i].y<=0+arrey[i].radius:
                arrey[i].dir_vec[1]=math.sqrt(arrey[i].dir_vec[1]**2)

        if hmsysteme.hit_detected():
            pos=hmsysteme.get_pos()
            pygame.draw.circle(screen, RED, [int(pos[0]),int(pos[1])],int(3/0.3), 5)
            pygame.display.flip()
            hmsysteme.take_screenshot(screen)
            for i in range(0,len(arrey)):
                if arrey[i].hit(pos):
                    print("gepoppt")
                    print(i)
        for event in pygame.event.get():            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                pygame.draw.circle(screen, RED, [int(pos[0]),int(pos[1])],int(3/0.3), 5)
                pygame.display.flip()
                hmsysteme.take_screenshot(screen)
                for i in range(0,len(arrey)):
                    if arrey[i].hit(pos):
                        print("gepoppt")
                        print(i)

        pygame.display.flip()
        #print(clock.get_fps())
        clock.tick(60)
    pygame.display.quit()     
    pygame.quit()
    
    
if __name__ == '__main__':
    main()

                
                

