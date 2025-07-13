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
    import led_calibration_temp
    import arduino_reset
    from shared_memory_dict import SharedMemoryDict


    path=os.path.realpath(__file__)
    path=path.replace('thread_handler.py', '')


    def led_calib(value):
        try:
            import smbus2
            bus=smbus2.SMBus(1)
            address = 0x2c
            bus.write_byte_data(address, 0, value)
            print("LEDS set to: " + str(value))
        except Exception as e:
            print(e)



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
    try:
        gamefiles.remove('__pycache__')
    except:
        pass
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
    activequeue = multiprocessing.Queue()

    #create shared memory to share data between processes
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

    if hmsysteme.check_ifdebug():
        pass#start these processes only if running on HM01 Hardware
    else:
        ths=multiprocessing.Process(target=hotspot.hotspot, args=("Mobile Hotspot",))
        ths.start()
        print("mobile hotspot process started")

        #t1 = multiprocessing.Process(target=led_calibration_temp.led_calibration_temp, args=("led_calibration_temp",tempqueue))
        #t1.start()
        #print("led calibration process started")
    

    t2 = multiprocessing.Process(target=hardware_com_micro.hardware_com_micro, args=("Hardware_com_micro", path, queue, queue4,prequeue,warmupqueue, size))
    t2.start()
    print("hardware_com_micro process started")

    t3 = multiprocessing.Process(target=startscreen.startscreen, args=("startscreen",warmupqueue,activequeue))

    t3.start()
    print("background process started")

    time.sleep(1)
    t4 = multiprocessing.Process(target=mobile_com.mobile_com, args=("Mobile_com", path, queuegamename, queue, queue2, queue3, queue4, queue5, prequeue, size, gamefiles, hwqueue,backgroundqueue,tempqueue,warmupqueue, activequeue))
    t4.start()
    print("mobile_com process started")

    while True:
        time.sleep(0.5)


        if str(hwqueue.get())=="off":
            t1.terminate()
            t1 = multiprocessing.Process(target=hardware_com_micro.hardware_com_micro, args=("Hardware_com", path, queue, queue4, size))
            time.sleep(0.5)
            t1.start()

if __name__ == '__main__':
    main()



