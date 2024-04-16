def rgb_background(threadname):
    try:
        import hmsysteme
        import time
        import smbus2
        bus=smbus2.SMBus(1)
        time.sleep(1)
        addrnano=0x1E
        bus.write_byte_data(addrnano, 0, 0)  # red
        bus.write_byte_data(addrnano, 1, 0)  # blue
        bus.write_byte_data(addrnano, 2, 0)  # green
    except Exception as e:
        print(e)
        return





    while True:
        time.sleep(0.5)
        a=hmsysteme.get_rgbcolor()     
        if a != False:
            try:
                bus.write_byte_data(addrnano,0, int(a[0]))#red
                bus.write_byte_data(addrnano, 1, int(a[2]))#blue
                bus.write_byte_data(addrnano, 2, int(a[1]))#green
                print("colors set")

            except Exception as e:
                print(e)
                print("only usable on HM01")
                print("color :" +str(a))


        hmsysteme.put_temp(bus.read_byte(addrnano))







