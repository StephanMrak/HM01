import multiprocessing
import queue
import pygame
import random
import functions_intern as hmsysteme
import logging


logger = logging.getLogger("template")
logger.info("Hello from template.py")


def get_rand_colour():
    colour_r = random.randint(0, 255)
    colour_g = random.randint(0, 255)
    colour_b = random.randint(0, 255)
    return (colour_r, colour_g, colour_b)


def main(ns_info, q_hit):
    # Get infos about the screen size and player names
    screen_size = ns_info.size
    the_players = ns_info.active_players
    logger.info(ns_info.active_players)
    logger.info(ns_info.all_players)
    hmsysteme.randomize_new_hit(ns_info)

    # Set the menu button names
    ns_info.buttons = ["button 1", "button 2"]

    # Set the background led color #TODO wofür ist das genau?
    ns_info.rgb = (123, 64, 23)

    # Pygame relevant things
    fps = 20
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(ns_info.size)
    if not ns_info.debug:
        pygame.mouse.set_visible(False)

    logger.info(ns_info)
    counter = 0
    colour = get_rand_colour()

    # Exit your game when 'ns_info.active' returns False
    # You might also exit your game when it is over.
    run = True
    while run:
        if (
            not ns_info.active
        ):  # Must be outside the event query. No events (like mouse movement) get generated when the winodw is in the background.
            run = False

        for event in pygame.event.get():
            if event.type == pygame.constants.QUIT:
                run = False
                break
                # TODO save the game state here
            elif event.type == pygame.constants.KEYDOWN:
                if event.key == pygame.constants.K_ESCAPE:
                    run = False
                elif event.key == pygame.constants.K_RETURN:
                    pass
            elif event.type == pygame.constants.MOUSEBUTTONDOWN:
                if ns_info.debug:
                    xy = pygame.mouse.get_pos()
                    print(xy)
                    pygame.draw.circle(screen, "red", xy, 5, 0)
                    hmsysteme.take_screenshot(screen)

        # check if a hit got detected
        # try:
        # x = q_hit.get_nowait()
        # print(x)
        # except queue.Empty:
        # pass

        counter += 1
        if counter > 10:
            colour = get_rand_colour()
            counter = 0

        screen.fill(colour)
        pygame.display.flip()

        dt = clock.tick(fps)
        pygame.display.flip()


if __name__ == "__main__":

    with multiprocessing.Manager() as manager:

        # ns_info contains all the important background infos like:
        # ns_info.playernames: list of all player names
        # ns_info.size: tuple with the sizes of the board (x, y)...
        ns_info = manager.Namespace()
        hmsysteme.initialize_info(ns_info)

        q_hit = multiprocessing.Queue(maxsize=1)

        main(ns_info=ns_info, q_hit=q_hit)
