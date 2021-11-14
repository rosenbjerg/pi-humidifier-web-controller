#!/usr/bin/python3

from flask import Flask
from threading import Event, Thread
import RPi.GPIO as GPIO

buttonPin = 23

rounds = 4
roundLengthSec = 7.0
roundDelaySec = 5.0

humidifying_ended = Event()
humidifying = False


def initialize():
    print('initializing')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buttonPin, GPIO.OUT)

    GPIO.output(buttonPin, GPIO.LOW)


def turn_on_humidifier():
    GPIO.output(buttonPin, GPIO.HIGH)


def turn_off_humidifier():
    GPIO.output(buttonPin, GPIO.LOW)


def turn_on():
    print('starting humidification')
    global humidifying
    if humidifying:
        print('humidifier is already started')
        return

    humidifying_ended.clear()
    humidifying = True

    for i in range(rounds):
        if not humidifying:
            break

        print('turning on humidifier')
        turn_on_humidifier()
        humidifying_ended.wait(roundLengthSec)

        print('turning off humidifier')
        turn_off_humidifier()
        humidifying_ended.wait(roundDelaySec)

    print('humidification completed')
    turn_off_humidifier()
    humidifying = False


def turn_off():
    print('stopping humidification')
    global humidifying
    humidifying = False
    humidifying_ended.set()


app = Flask(__name__)


@app.route('/')
def online():
    return 'OK'


@app.route('/humidifier/on')
def humidifier_on():
    Thread(target=turn_on).start()
    return 'On'


@app.route('/humidifier/off')
def humidifier_off():
    turn_off()
    return 'Off'


if __name__ == '__main__':
    initialize()
    print('starting hosting')
    app.run(host='0.0.0.0')
    GPIO.cleanup()
