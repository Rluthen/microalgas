#!/usr/bin/env pyhton

import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
LED = 18
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)


try:
	while True:
		print("Place tag to read")
		id, text = reader.read()
		print(id)
		print(text)
		GPIO.output(LED, GPIO.HIGH)
		time.sleep(2)
		GPIO.output(LED, GPIO.LOW)
except KeyboardInterrupt:
	GPIO.cleanup()
	raise
