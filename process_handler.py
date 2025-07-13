def main():
    import time
    import multiprocessing
    import sys
    import os
    import hardware_com_micro
    import mobile_com
    import hotspot
    import startscreen
    import hmsysteme
    import argparse
    from shared_memory_dict import SharedMemoryDict

    process_parser = argparse.ArgumentParser(description='Start the HM01 Shooting Range.')
    process_parser.add_argument('--debug', action='store_true', help='Enable debug output.')
    args = process_parser.parse_args()

    if args.debug:
        print('Debug mode is enabled.')
    else:
        print('Debug mode is disabled.')

    path = os.path.realpath(__file__)
    path = path.replace('process_handler.py', '')


    sys.path.append(os.path.join(path, "games"))


    def list_files(path='.'):
        for filename in os.listdir(path):
            if os.path.isfile(os.path.join(path, filename)):
                print(filename)
            else:
                list_files(os.path.join(path, filename))

    gamefiles = os.listdir(os.path.join(path, "games"))
    try:
        gamefiles.remove('__pycache__')
    except:
        pass
    gamefiles.remove('game_template.py')
    gamefiles.remove('pics')

    for x in range(len(gamefiles)):
        gamefiles[x] = gamefiles[x].replace('.py', '')

    modules = []
    for x in gamefiles:
        try:
            modules.append(__import__(x))
            print("Successfully imported", x, '.')
        except ImportError:
            print("Error importing", x, '.')
    print(gamefiles)

    backgroundqueue = multiprocessing.Queue(maxsize=1)


    # create shared memory to share data between processes
    hmsysteme.create_shared_memory()
    smd = SharedMemoryDict(name='data', size=1024)
    smd["Active"] = False
    smd["Hit"] = False
    smd["Pos"] = False
    smd["Players"] = False
    smd["Screen"] = False
    smd["RGB"] = False
    smd["Temp"] = False
    smd["Action"] = False
    smd["Buttons"] = False

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

    t3 = multiprocessing.Process(target=startscreen.startscreen, args=("startscreen",args.debug))
    t3.start()
    print("background process started")

    time.sleep(1)
    t4 = multiprocessing.Process(target=mobile_com.mobile_com,
                                 args=("Mobile_com", path, gamefiles, backgroundqueue,args.debug))
    t4.start()
    print("mobile_com process started")



if __name__ == '__main__':
    main()



