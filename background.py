def background(threadhandler, backgroundqueue, warmupqueue, activequeue):
    import pygame
    import time
    import os
    import sys
    import hmsysteme

    WHITE = (255, 255, 255)
    size = hmsysteme.get_size()
    path = os.path.realpath(__file__)
    path = path.replace("background.py", "")
    print(path)
    a = "init"
    clock = pygame.time.Clock()
    warmuptime = 0
    # screen = pygame.display.set_mode(size)
    # screen.fill(WHITE)
    running = False

    while True:
        # time.sleep(0.1)
        if not backgroundqueue.empty():
            a = backgroundqueue.get()

        if a == "open":
            print("background opened")
            pygame.init()

            if hmsysteme.check_ifdebug():
                screen = pygame.display.set_mode(size)
            else:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

            running = True
            a = "init"

        if running == True:
            screen.fill(WHITE)

            for event in pygame.event.get():
                # Beenden bei [ESC] oder [X]
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    pygame.display.quit()
                    pygame.quit()
            image1 = pygame.image.load(os.path.join(path, "login_info.jpg"))
            # screen = pygame.display.set_mode(size)

            screen.blit(
                image1, [(size[0] - image1.get_width()) / 2, (size[1] - image1.get_height()) / 2]
            )

            # print("0")
            if not warmupqueue.empty():
                warmuptime = warmupqueue.get()

            if warmuptime > 0:
                os.environ["hm_LEDsWarmupComplete"] = "0"
                GAME_FONT = pygame.font.SysFont("Times", 50)
                # print(warmuptime)
                text = GAME_FONT.render(
                    "LEDs auf Betriebstemperatur bringen: " + str(warmuptime), True, (255, 0, 0)
                )
                screen.blit(text, (150, 150))
                del GAME_FONT
            else:
                activequeue.put(True)

            pygame.mouse.set_visible(False)
            pygame.display.flip()
            clock.tick(10)

        if a == "close":
            print("background closed")
            pygame.display.quit()
            pygame.quit()
            a = "init"
            running = False
        a = "init"


if __name__ == "__main__":
    background()
