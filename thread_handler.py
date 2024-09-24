def main():

    import time
    import multiprocessing
    import sys
    import os
    import hardware_com
    import mobile_com
    import hotspot
    import background
    import rgb_background
    import hmsysteme
    import led_calibration_temp
    import arduino_reset
    import psutil
    import logging

    path=os.path.realpath(__file__)
    path=path.replace('thread_handler.py', '')
    #log_file=os.path.isfile(os.path.join(path, "logfilename.log"))
    #logging.basicConfig(filename="logfile.txt",format='%(asctime)s %(levelname)-8s %(message)s',
    #    level=logging.DEBUG,
    #    datefmt='%Y-%m-%d %H:%M:%S')

    #logger=logging.getLogger()
    #logger.debug("Debug")
    #print("Info")
    #logger.warning("Warning")
    #logger.error("Error")
    #logger.critical("Critical")

    def led_calib(value):
        try:
            import smbus2
            bus=smbus2.SMBus(1)
            address = 0x2c
            bus.write_byte_data(address, 0, value)
            print("LEDS set to: " + str(value))
        except Exception as e:
            print(e)
            
    #led_calib(200)

    def is_raspberrypi():
        try:
            import RPi.GPIO as gpio
            return True
        except (ImportError, RuntimeError):
            return False
    def is_connected_to_lan():
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        available_networks = []
        for intface, addr_list in addresses.items():
            if any(getattr(addr, 'address').startswith("169.254") for addr in addr_list):
                continue
            elif intface in stats and getattr(stats[intface], "isup"):
                available_networks.append(intface)
            if intface.find("eth0") != -1:
                if getattr(stats[intface], "speed") == 65535:
                    print("Starting Interface")                    
                else:
                    return
                    


    print("")


    hmsysteme.clear_all()

    arduino_reset.arduino_reset()


    sys.path.append(os.path.join(path, "games"))
    size=hmsysteme.get_size()

    def list_files(path='.'):
        for filename in os.listdir(path):
            if os.path.isfile(os.path.join(path, filename)):
                print(filename)
            else:
                list_files(os.path.join(path, filename))

    gamefiles=os.listdir(os.path.join(path, "games"))
    gamefiles.remove('__pycache__')
    gamefiles.remove('game_template.py')
    gamefiles.remove('pics')

    for x in range(len(gamefiles)):
        gamefiles[x]=gamefiles[x].replace('.py', '')

    modules=[]
    for x in gamefiles:
        try:
            modules.append(__import__(x))
            print("Successfully imported", x, '.')
        except ImportError:
            print("Error importing", x, '.')
    print(gamefiles)

    queue=multiprocessing.Queue()
    queue2=multiprocessing.Queue()
    queue3=multiprocessing.Queue(maxsize = 1)
    queue4=multiprocessing.Queue()
    queue5=multiprocessing.Queue(maxsize = 1)
    hwqueue=multiprocessing.Queue(maxsize = 1)
    backgroundqueue=multiprocessing.Queue(maxsize = 1)
    tempqueue = multiprocessing.Queue(maxsize=1)
    queuegamename = []
    prequeue = multiprocessing.Queue()
    warmupqueue = multiprocessing.Queue()


    ths=multiprocessing.Process(target=hotspot.hotspot, args=("Mobile Hotspot",))
    ths.start()
    print("mobile hotspot process started")
    
    #t1 = multiprocessing.Process(target=led_calibration_temp.led_calibration_temp, args=("led_calibration_temp",tempqueue))
    #t1.start()
    #print("led calibration process started")
    
    #time.sleep(1)
    t2 = multiprocessing.Process(target=hardware_com.hardware_com, args=("Hardware_com", path, queue, queue4,prequeue,warmupqueue, size))
    t2.start()
    print("hardware_com process started")

    #t3 = multiprocessing.Process(target=background.background, args=("background",backgroundqueue,warmupqueue))
    #t3.start()
    #print("background process started")

    time.sleep(1)
    t4 = multiprocessing.Process(target=mobile_com.mobile_com, args=("Mobile_com", path, queuegamename, queue, queue2, queue3, queue4, queue5, prequeue, size, gamefiles, hwqueue,backgroundqueue,tempqueue,warmupqueue))
    t4.start()
    print("mobile_com process started")





    while True:
        time.sleep(0.5)
        if str(hwqueue.get())=="off":
            t1.terminate()
            t1 = multiprocessing.Process(target=hardware_com.hardware_com, args=("Hardware_com", path, queue, queue4, size))
            time.sleep(0.5)
            t1.start()
		
    

if __name__ == '__main__':
    main()



