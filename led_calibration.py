def led_calibration(threadname):
    import smbus2
    import time

    bus = smbus2.SMBus(1)
    address = 0x2C
    bus.write_byte_data(address, 0, 201)


if __name__ == "__main__":

    led_calibration("thread")
