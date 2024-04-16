import smbus2
import time

while:
    time.sleep(1)
    bus = smbus2.SMBus(1)
    addrnano = 0x1E
    bus.write_byte_data(addrnano, 0, 22)