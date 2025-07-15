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
    x_1=0
    y_1=0
    #some colors to use
    BLACK = ( 0, 0, 0)
    WHITE = ( 255, 255, 255)
    GREEN = ( 0, 255, 0)
    BLUE = (0,191,255)
    RED = ( 255, 0, 0)
    size=hmsysteme.get_size()
    pygame.init()
    pygame.font.init()
    screen=pygame.display.set_mode(size)
    pygame.mouse.set_visible(False)     
    clock = pygame.time.Clock()
    print("players")
    print(hmsysteme.get_playernames())

   
    while hmsysteme.game_isactive():
        #print(hmsysteme.get_playernames())
        screen.fill(BLACK)
#            #print something to the pygame window
#            font = pygame.font.SysFont(pygame.font.get_fonts()[0], 72)
#            #text to be printed to screen
#            text = font.render(str("print to screen"), True, (0, 128, 0))
#            screen.blit(text,(320 - text.get_width() // 2, 240 - text.get_height() // 2))
#            #delete created font to avoid pygame bug
#            del font

        if hmsysteme.hit_detected() == True: 
            #get bullet coordinates in pixels from 'hardware_com'
            #the coordiante origin is bottom left
            xy=hmsysteme.get_pos()
            x_1=float(xy[0])
            y_1=float(xy[1])
            print(xy)
            hit=True
        #create your game here
        pygame.draw.circle(screen, RED, [int(x_1),int(y_1)],int(3/0.3), 5)
        zaehler=0
        radius=50
        fontheight=radius
        font = pygame.font.Font(None, 28)
        for i in range(radius,size[0]-radius,200):
            for j in range(radius,size[1]-radius,200):
                #print(i,j)
                zaehler=zaehler+1
                pygame.draw.circle(screen, WHITE, [i,j],radius, 5)
                text = font.render(str(zaehler), True, WHITE)
                screen.blit(text,(i-fontheight/2, j-fontheight/2))
        del font
                
        #   
        #
        #.....

        
        #check if the screen has been hit by a bullet
        if hit==True:
            hit=False
            hmsysteme.take_screenshot(screen)
            #safe screenshot of bullet location
        pygame.display.flip()
        clock.tick(60)
    #close pygame window    
    pygame.font.quit()
    pygame.display.quit()    
    pygame.quit() 

if __name__ == '__main__':
    main()