def main():
    import time
    import multiprocessing
    import sys
    import os
    import hardware_com_micro
    import mobile_com
    import hotspot
    import startscreen
    import argparse
    import hmsysteme

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


    if args.debug:
        pass
    else:
        ths = multiprocessing.Process(target=hotspot.hotspot, args=("Mobile Hotspot",))
        ths.start()
        print("mobile hotspot process started")


    t2 = multiprocessing.Process(target=hardware_com_micro.hardware_com_micro,
                                 args=("Hardware_com_micro",args.debug))
    t2.start()
    print("hardware_com_micro process started")

    t3 = multiprocessing.Process(target=startscreen.startscreen, args=("startscreen",backgroundqueue,args.debug))
    t3.start()
    print("background process started")

    time.sleep(1)
    t4 = multiprocessing.Process(target=mobile_com.mobile_com,
                                 args=("Mobile_com", path, gamefiles, backgroundqueue,args.debug))
    t4.start()
    print("mobile_com process started")

    def gpio_callback(channel):
        if not GPIO.input(BUTTON_GPIO):
            hmsysteme.set_busy(True)
            print("busy True")
        else:
            hmsysteme.set_busy(False)
            print("busy False")


    try:
        import RPi.GPIO as GPIO
        BUTTON_GPIO = 16
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH,
                              callback=gpio_callback, bouncetime=50)

    except:
        pass




if __name__ == '__main__':
    main()



