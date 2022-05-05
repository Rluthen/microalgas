import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from time import sleep
from random import randint
import fysom
from fysom import *
import serial
from update_stock import update_stock

ser_scale = serial.Serial('/dev/ttyACM0')
reader = SimpleMFRC522()
LED_READY = 16
LED_READING = 15
LED_SENDING = 13
LED_ERROR = 11
LED = 18
error_flag = 0
read_tag = 0
scale_float = 0

GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(3, GPIO.FALLING)

GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

GPIO.setup(LED_READY, GPIO.OUT)
GPIO.output(LED_READY, GPIO.LOW)

GPIO.setup(LED_READING, GPIO.OUT)
GPIO.output(LED_READING, GPIO.LOW)

GPIO.setup(LED_SENDING, GPIO.OUT)
GPIO.output(LED_SENDING, GPIO.LOW)

GPIO.setup(LED_ERROR, GPIO.OUT)
GPIO.output(LED_ERROR, GPIO.LOW)

def get_scale():
    global error_flag
    if ser_scale.is_open == 0:
        ser_scale.open()
    
    ser_scale.write(b'P')
    scale_str = ser_scale.read(6)
    scale_str = scale_str[1:6]
    print('String:', scale_str)
    if scale_str == b' NEG.':
        error_flag = 1
    else:
        scale_float = float(scale_str)
        print('Float:', scale_float)
        if scale_float == 0:
            error_flag = 2
    ser_scale.close()
    
def onready():
	print('Ready')
	GPIO.output(LED_READY, GPIO.HIGH)
	GPIO.output(LED_READING, GPIO.LOW)
	GPIO.output(LED_SENDING, GPIO.LOW)
	GPIO.output(LED_ERROR, GPIO.LOW)

def onreading():
    global read_tag
    global error_flag
    print('Reading')
    GPIO.output(LED_READING, GPIO.HIGH)
    GPIO.output(LED_READY, GPIO.LOW)
    GPIO.output(LED_SENDING, GPIO.LOW)
    
    id, text = reader.read()
    id = 1234
    print(id)
    if id == 0:
        error_flag = 3
    else:
        GPIO.output(LED, GPIO.HIGH)
        sleep(2) 
        GPIO.output(LED, GPIO.LOW)
    if error_flag == 0:
        get_scale()
        if error_flag == 0:
            read_tag = 1

def onsending():
    print('Sending\n')
    GPIO.output(LED_SENDING, GPIO.HIGH)
    GPIO.output(LED_READY, GPIO.LOW)
    GPIO.output(LED_READING, GPIO.LOW)
    sleep(3)
	#fsm.err()

def onerror():
    global error_flag
    print('Error\n')
    GPIO.output(LED_ERROR, GPIO.HIGH)
    if error_flag == 1:
        print('Calibra la bascula')
    if error_flag == 2:
        print('Coloca algo en la bascula')
    if error_flag == 3:
        print('NO HAY TAG')
    if error_flag == 4:
        print('Error al enviar')
    error_flag = 0
    sleep(2)

# 
fsm = Fysom({'initial' : 'ready',
            'events' : [
                {'name': 'start','src': 'ready','dst' :'reading'},
                {'name': 'done_r','src': 'reading','dst' :'sending'},
                {'name': 'err','src': 'reading','dst' :'error'},
                {'name': 'done_s','src': 'sending','dst' :'ready'},
                {'name': 'err','src': 'sending','dst' :'error'},
                {'name': 'reset','src': 'error','dst' :'ready'}]})
#             'callbacks' : {
#                     'onready': onready,
#                     'onreading': onreading,
#                     'ondone_r': onsending,
#                     'onerror': onerror}})


def start(e):
    if fsm.current == 'ready':
        sleep(1)
        fsm.start()
    
GPIO.add_event_callback(3, start)

try:
    while True:
        if fsm.current == 'ready':
            onready()
        if fsm.current == 'error':
            print('imposible')
        if (fsm.current == 'reading'):
            onreading()
            if error_flag != 0:
                fsm.err()
            else:
                if read_tag == 1:
                    fsm.done_r()
                    read_tag = 0     
        if fsm.current == 'sending':
            onsending()
            try:
                update_stock(read_tag,scale_float)
            except Exception as e:
                    error_flag = 4
            fsm.done_s()
        if fsm.current == 'error':
            onerror()
            fsm.reset()
except KeyboardInterrupt:
	GPIO.cleanup()
	raise   
    
# def onpanic(e):
#     print ('panic! ' + e.msg)
# def oncalm(e):
#     print ('thanks to ' + e.msg + ' done by ' + e.args[0])
# def ongreen(e):
#     print ('green')
#     fsm.clear()
# def onyellow(e):
#     print ('yellow')
# def onred(e):
#     print ('red')
#     
# fsm = Fysom({'initial': 'green',
#            'events': [
#                {'name': 'warn', 'src': 'green', 'dst': 'yellow'},
#                {'name': 'panic', 'src': 'yellow', 'dst': 'red'},
#                {'name': 'panic', 'src': 'green', 'dst': 'red'},
#                {'name': 'calm', 'src': 'red', 'dst': 'yellow'},
#                {'name': 'clear', 'src': 'yellow', 'dst': 'green'}],
#            'callbacks': {
#                'onpanic': onpanic,
#                'oncalm': oncalm,
#                'ongreen': ongreen,
#                'onyellow': onyellow,
#                'onred': onred }})
# 
# fsm.panic(msg='killer bees')
# fsm.calm('bob', msg='sedatives in the honey pots')
