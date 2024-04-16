def hotspot(threadname):
    import os
    import time
    try:
        os.system("sudo rfkill unblock wlan")
        time.sleep(1)
    #os.system("sudo service hostapd restart")
    #time.sleep(1)
    #os.system("sudo service dnsmasq restart")
    #time.sleep(1)
        os.system("sudo hostapd /etc/hostapd/hostapd.conf")
    except Exception as e:
        print(e)
