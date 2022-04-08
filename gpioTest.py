import RPi.GPIO as GPIO

import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(13, GPIO.IN)

"""
while(True):
    GPIO.output(7,True)
    time.sleep(1)
    GPIO.output(7,False)
    time.sleep(1)
    print("e")
"""
while(True):
    if GPIO.input(13)==1:
        GPIO.output(7, True)
    else:
        GPIO.output(7, False)

GPIO.cleanup()