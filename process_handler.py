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
    import WiFiHelper
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


    # Initialize the WiFi helper
    wifi = WiFiHelper.WiFiHelper(log_level=logging.DEBUG)
    
    # Check if setup has been completed
    if not wifi._check_setup_complete():
        print("WARNING: Setup not complete. Please run setup_wifi_helper.sh first!")
        print("sudo bash setup_wifi_helper.sh $USER")
        print("")
    
    # Check current mode
    mode = wifi.get_current_mode()
    print(f"Current mode: {mode}")
    
    # Check internet connection
    ssid = None
    passw = None
    encryption = None
    if wifi.check_internet_connection():
        print("Internet connection available")
        ssid = wifi.get_current_ssid()
        pw = "Your Wifi Password"
        if ssid:
            print(f"Connected to: {ssid}")
            creds = wifi.get_current_network_credentials()
            if creds:
                ssid = creds["ssid"]
                passw = creds["password"]
                encryption = creds["encryption"]
    else:
        print("No internet connection")
        # Create a hotspot if not already in hotspot mode
        if mode != "hotspot":
            print("\nCreating hotspot...")
            ssid_attempt = "ShootingRange"
            pw_attempt = "123456"
            success = wifi.create_hotspot(
                ssid=ssid_attempt,
                password=pw_attempt,
                country="DE",  # Change to your country code
                channel=7,
                enable_nat=True
            )
            
            if success:
                # TODO: is it really WPA?
                ssid = ssid_attempt
                passw = pw_attempt
                encryption = "WPA"
                print("Hotspot created successfully!")
                print("Connect to WiFi: ShootingRange")
                print("Password: 123456")
                print("Then access: http://192.168.4.1")



    t2 = multiprocessing.Process(target=hardware_com_micro.hardware_com_micro,
                                 args=("Hardware_com_micro",args.debug))
    t2.start()
    print("hardware_com_micro process started")

    t3 = multiprocessing.Process(target=startscreen.startscreen, args=(ssid, passw))
    t3.start()
    print("background process started")

    time.sleep(1)
    t4 = multiprocessing.Process(target=mobile_com.mobile_com,
                                 args=("Mobile_com", path, gamefiles, backgroundqueue, args.debug))
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



