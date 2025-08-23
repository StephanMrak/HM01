def main():
    global mausx,mausy,hit_for_screenshot
    global shot_positions,show_last_shots,show_coordinates,iGetAction
    import pygame
    import time
    import hmsysteme
    import os
    import platform
    import random
    import pygame.freetype
    hmsysteme.put_button_names(["SHOTS: 5", "COORDS: ON", "TEST SHOT", "x", "x", "x", "x", "x", "x"])
    print(platform.uname())
    pygame.init()

    #size = [1366, 768]
    size = hmsysteme.get_size()

    path = os.path.realpath(__file__)
    #    path = path.replace('Prestige\Prestige.py', '')
    if 'Linux' in platform.uname():
        path = path.replace('PositionTest.py', '')
    else:
        path = path.replace('PositionTest.py', '')

    #screen = pygame.display.set_mode(size)
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    clock = pygame.time.Clock()
    pygame.display.set_caption("Position Test")

    #TextFonds
    TXT_COORDS = pygame.font.SysFont("Times", 24)
    TXT_TITLE = pygame.font.SysFont("Times", 36)

    ############Variablen###########
    BACKGROUND_COLOR = (50, 50, 50)
    SHOT_COLORS = [
        (255, 0, 0),    # Red
        (255, 128, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 255, 255),  # Cyan
        (0, 0, 255),    # Blue
        (255, 0, 255),  # Magenta
        (128, 128, 128), # Gray
        (255, 192, 203), # Pink
        (165, 42, 42)   # Brown
    ]
    framerate = 30
    mausx = 0
    mausy = 0
    hit_for_screenshot = False
    shot_positions = []
    show_last_shots = 5
    show_coordinates = True
    iGetAction = 0

    def zeichnen():
        global shot_positions,show_last_shots,show_coordinates
        
        screen.fill(BACKGROUND_COLOR)
        
        txtTitle = TXT_TITLE.render(f"Position Test - Showing last {show_last_shots} shots", True, (255, 255, 255))
        screen.blit(txtTitle, (20, 20))
        
        for i in range(min(show_last_shots, len(shot_positions))):
            pos_index = len(shot_positions) - min(show_last_shots, len(shot_positions)) + i
            x, y = shot_positions[pos_index]
            screen_x = int(x * 1000)
            screen_y = int(y * 1000)
            
            screen_x = max(10, min(size[0] - 10, screen_x))
            screen_y = max(60, min(size[1] - 10, screen_y))
            
            if i == min(show_last_shots, len(shot_positions)) - 1:
                color = (255, 0, 0)  # Red for latest shot
            else:
                color = (255, 255, 255)  # White for all other shots
            
            dot_size = 15
            pygame.draw.circle(screen, color, (screen_x, screen_y), dot_size)
            pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), dot_size, 2)
            
            if show_coordinates:
                txtCoord = TXT_COORDS.render(f"({x:.3f}, {y:.3f})", True, (255, 255, 255))
                text_x = screen_x + dot_size + 5
                text_y = screen_y - 12
                
                pygame.draw.rect(screen, (0, 0, 0), [text_x-2, text_y-2, 120, 25], 0)
                screen.blit(txtCoord, (text_x, text_y))
        
        legend_y = size[1] - 100
        txtLegend = TXT_COORDS.render("Settings:", True, (255, 255, 255))
        screen.blit(txtLegend, (20, legend_y))
        
        txtSetting1 = TXT_COORDS.render(f"Show last shots: {show_last_shots}", True, (200, 200, 200))
        screen.blit(txtSetting1, (20, legend_y + 25))
        
        txtSetting2 = TXT_COORDS.render(f"Show coordinates: {'ON' if show_coordinates else 'OFF'}", True, (200, 200, 200))
        screen.blit(txtSetting2, (20, legend_y + 50))
        
        txtSetting3 = TXT_COORDS.render(f"Total shots recorded: {len(shot_positions)}", True, (200, 200, 200))
        screen.blit(txtSetting3, (20, legend_y + 75))
        
        pygame.display.flip()

    def reset_parameter():
        global mausx,mausy
        mausx = 0
        mausy = 0

    def ButtonHandler():
        global iGetAction,show_last_shots,show_coordinates,shot_positions
        iGetAction = hmsysteme.get_action()
        if iGetAction > 0:
            if iGetAction == 1:
                if show_last_shots == 1:
                    show_last_shots = 3
                elif show_last_shots == 3:
                    show_last_shots = 5
                elif show_last_shots == 5:
                    show_last_shots = 10
                elif show_last_shots == 10:
                    show_last_shots = len(shot_positions) if len(shot_positions) > 0 else 1
                else:
                    show_last_shots = 1
                    
                if show_last_shots == len(shot_positions) and len(shot_positions) > 10:
                    hmsysteme.put_button_names(["SHOTS: ALL", "COORDS: ON" if show_coordinates else "COORDS: OFF", "TEST SHOT", "x", "x", "x", "x", "x", "x"])
                else:
                    hmsysteme.put_button_names([f"SHOTS: {show_last_shots}", "COORDS: ON" if show_coordinates else "COORDS: OFF", "TEST SHOT", "x", "x", "x", "x", "x", "x"])
                    
            if iGetAction == 2:
                show_coordinates = not show_coordinates
                button_text = f"SHOTS: {show_last_shots}" if show_last_shots != len(shot_positions) or len(shot_positions) <= 10 else "SHOTS: ALL"
                hmsysteme.put_button_names([button_text, "COORDS: ON" if show_coordinates else "COORDS: OFF", "TEST SHOT", "x", "x", "x", "x", "x", "x"])
                
            if iGetAction == 3:
                test_x = random.uniform(0.1, 1.3)
                test_y = random.uniform(0.1, 0.8)
                shot_positions.append((test_x, test_y))
                print(f"Test shot generated at: ({test_x:.3f}, {test_y:.3f})")

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
                mausx = event.pos[0]
                mausy = event.pos[1]
                print("X: ", mausx, "Y: ", mausy)

        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            mausx = pos[0] * 1000 if pos else 0
            mausy = pos[1] * 1000 if pos else 0
            if pos and len(pos) >= 2:
                x, y = pos[0], pos[1]
                shot_positions.append((x, y))
                print(f"Hit detected at position: ({x:.3f}, {y:.3f})")
                reset_parameter()

        # Screenshot
        if hit_for_screenshot:
            pygame.display.flip()
            hmsysteme.take_screenshot(screen)
            hit_for_screenshot = False

        #Zeichnen
        zeichnen()
        clock.tick(framerate)

if __name__ == '__main__':
    main()
