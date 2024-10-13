def led_calibration_temp(threadname, tempqueue):
    import hmsysteme
    import time
    import statistics
    import math
    import smbus2

    bus = smbus2.SMBus(1)
    LED_value = 200

    def measuretemp():
        try:
            s = []
            for i in range(0, 20):
                time.sleep(1)
                temp = hmsysteme.get_temp()
                if temp != False:
                    s.append(temp)
            # print(s)
            s = statistics.median(s)
            s = int(round(s, 0))
            print("temp :" + str(s))
            return s
        except:
            pass

    def led_calib(value):
        try:
            address = 0x2C
            bus.write_byte_data(address, 0, value)
            print("LEDS set to: " + str(value))
        except Exception as e:
            print(e)

    try:
        time.sleep(1)
        addrnano = 0x1E
        bus.write_byte_data(addrnano, 0, 0)  # red
        bus.write_byte_data(addrnano, 1, 0)  # blue
        bus.write_byte_data(addrnano, 2, 0)  # green
        led_calib(LED_value)
        time.sleep(1)
        hmsysteme.put_temp(bus.read_byte(addrnano))
        time.sleep(1)
        temp_init = hmsysteme.get_temp()
        print("init temp :" + str(temp_init))
        time.sleep(1)
    except Exception as e:
        print(e)

    while True:
        try:
            # hmsysteme.put_temp(bus.read_byte(addrnano))
            time.sleep(0.1)
            s = bus.read_byte(addrnano)
            # s=hmsysteme.get_temp()
            # print(s)

            s = int(round(s, 0))
            # a = LED_value + 3 * (s - temp_init)
            a = LED_value
            # if a>200:
            #    a=200
            tempqueue.put("temp: " + str(s) + " val:" + str(a))

            # led_calib(a)

            time.sleep(0.5)
            b = hmsysteme.get_rgbcolor()
            if b != False:
                try:
                    bus.write_byte_data(addrnano, 0, int(b[0]))  # red
                    bus.write_byte_data(addrnano, 1, int(b[2]))  # blue
                    bus.write_byte_data(addrnano, 2, int(b[1]))  # green
                    print("colors set")

                except Exception as e:
                    print(e)
                    print("only usable on HM01")
                    print("color :" + str(b))

        except Exception as e:
            print(e)
