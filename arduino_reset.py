def arduino_reset():
	import time
	try:
		import RPi.GPIO as GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(14, GPIO.OUT)
		GPIO.output(14, 0)
		time.sleep(0.1)
		GPIO.output(14, 1)
		time.sleep(5)
		print("arduino reset")
	except:
		pass



