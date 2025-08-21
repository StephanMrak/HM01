def main():
    import time
    import multiprocessing
    import sys
    import os
    import mobile_com
    import argparse
    import hmsysteme
    import logging

    process_parser = argparse.ArgumentParser(description='Start the HM01 Shooting Range.')
    process_parser.add_argument('--debug', action='store_true', help='Enable debug output.')
    args = process_parser.parse_args()

    if args.debug:
        print('Debug mode is enabled.')
    else:
        print('Debug mode is disabled.')
    hmsysteme.set_debug(args.debug)
    path = os.path.realpath(__file__)
    path = path.replace('process_handler.py', '')
    sys.path.append(os.path.join(path, "games"))
    gamesdir = os.listdir(os.path.join(path, "games"))

    gamefiles = []

    for game in gamesdir:
        if game.endswith(".py"):
            gamefiles.append(game.replace('.py', ''))

    backgroundqueue = multiprocessing.Queue(maxsize=1)

    t4 = multiprocessing.Process(target=mobile_com.mobile_com,
                                 args=("Mobile_com", path, gamefiles, backgroundqueue, args.debug))
    t4.start()
    print("mobile_com process started")

if __name__ == '__main__':
    main()



