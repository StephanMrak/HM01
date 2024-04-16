def main(): 
    import time
    import pygame
    import math
    import random
    import os
    import sys
    import hmsysteme
    hit=False
    carryOn=False
    #some colors to use
    BLACK = ( 0, 0, 0)
    WHITE = ( 255, 255, 255)
    GREEN = ( 0, 255, 0)
    BLUE = (0,191,255)
    RED = ( 255, 0, 0)
    x_1 = 0
    y_1 = 0
    pygame.init()
    size=hmsysteme.get_size()
    screen=pygame.display.set_mode(size, pygame.NOFRAME)
    pygame.display.set_caption("my game")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()



    while hmsysteme.game_isactive():
        screen.fill(WHITE)
        print(hmsysteme.get_temp())
        if hmsysteme.hit_detected():
            xy=hmsysteme.get_pos()
            #get bullet coordinates in pixels from 'hardware_com'
            #the coordiante origin is bottom left
            x_1=float(xy[0])
            y_1=float(xy[1])
            print(xy)
            hit=True
        #create your game here
        pygame.draw.circle(screen, RED, [int(x_1),int(y_1)],int(3/0.3), 5)
        pygame.draw.circle(screen, BLUE, [int(size[0]-300),int(size[1]-300)],int(3/0.3), 5)
        pygame.draw.circle(screen, BLACK, [int(size[0]-250),int(size[1]-450)],int(3/0.3), 5)
        pygame.draw.circle(screen, GREEN, [int(size[0]-100),int(size[1]-350)],int(3/0.3), 5)
        #.....

        
        #check if the screen has been hit by a bullet
        if hit==True:
            hit=False
            print("IST: X: " , x_1, "Y:", y_1, "SOLL Blau: X: ", size[0]-300, "Y: ",size[1]-500,
                  "SOLL Schwarz: X: ", size[0]-250, "Y: ",size[1]-450,
                  "SOLL Grün: X: ", size[0]-100, "Y: ",size[1]-350)
            hmsysteme.take_screenshot(screen)
            #safe screenshot of bullet location
            #os.remove(os.path.join(path,"screencapture.png"))
            #pygame.image.save(screen, os.path.join(path,"screencapture.png"))

        pygame.display.flip()
        clock.tick(60)
    #close pygame window    
    pygame.font.quit()
    pygame.display.quit()    
    pygame.quit() 

