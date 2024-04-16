def game(threadname,path,qgn,q,q3,size): 
    import time
    import pygame
    import math
    import random
    import os
    import sys
    hit=False
    carryOn=False
    #some colors to use
    BLACK = ( 0, 0, 0)
    WHITE = ( 255, 255, 255)
    GREEN = ( 0, 255, 0)
    BLUE = (0,191,255)
    RED = ( 255, 0, 0)
    x_1=0
    y_1=0

    while True:        
        time.sleep(0.1)
        if not qgn.empty():
            if str(qgn.get())=="y":
                #init pygame from User Interface
                carryOn=True
                pygame.init()
                pygame.font.init()
                screen=pygame.display.set_mode(size, pygame.NOFRAME)
                pygame.mouse.set_visible(False)     
                clock = pygame.time.Clock()
            else:
                carryOn=False

        while carryOn:
            screen.fill(WHITE)
            if not qgn.empty():
                if str(qgn.get())=="x":
                    #leave pygame while loop 
                    carryOn=False
            #print something to the pygame window
            font = pygame.font.SysFont(pygame.font.get_fonts()[0], 72)
            #text to be printed to screen
            text = font.render(str("print to screen"), True, (0, 128, 0))
            screen.blit(text,(320 - text.get_width() // 2, 240 - text.get_height() // 2))
            #delete created font to avoid pygame bug
            del font

            if not q.empty():
                #get bullet coordinates in pixels from 'hardware_com'
                #the coordiante origin is bottom left
                xy=q.get()
                x_1=float(xy[0])
                y_1=float(xy[1])
                print(xy)
                hit=True
            #create your game here
            #   
            #
            #.....

            
            #check if the screen has been hit by a bullet
            if hit==True:
                hit=False
                #safe screenshot of bullet location
                os.remove(os.path.join(path,"screencapture.png"))
                pygame.image.save(screen, os.path.join(path,"screencapture.png"))
                if not q3.full():
                    q3.put("refresh")
            pygame.display.flip()
            clock.tick(60)
        #close pygame window    
        pygame.font.quit()
        pygame.display.quit()    
        pygame.quit() 

