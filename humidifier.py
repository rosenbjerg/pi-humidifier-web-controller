#!/usr/bin/python3

from dotenv import load_dotenv
from flask import Flask
from threading import Event, Thread
import RPi.GPIO as GPIO
import requests
import os

button_pin = 23
fan_pin = 24

rounds = 4
roundLengthSec = 7.0
roundDelaySec = 3.0

usage_ended = Event()
actively_using = False


load_dotenv()
hass_token = os.getenv('HASS_TOKEN')
hass_host = os.getenv('HASS_HOST')
humidifier_entity_id = os.getenv('HASS_HUMIDIFIER_ENTITY_ID')
fan_entity_id = os.getenv('HASS_FAN_ENTITY_ID')

humidifier_icon = 'mdi:sprinkler-variant'
humidifier_name = 'Plant Humidifier'
fan_icon = 'mdi:fan'
fan_name = 'Plant Fan'

def report_to_homeassistant(entity_id, state, name, icon):
    global hass_token
    global hass_entity_id
    global hass_host
    if hass_token is not None:
        requests.post(f'http://{hass_host}/api/states/{entity_id}', headers={'Authorization': f'Bearer {hass_token}'}, json={"state": state, "attributes": {"friendly_name": name, "icon": icon}})

def initialize():
    print('initializing')
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(button_pin, GPIO.OUT)
    GPIO.output(button_pin, GPIO.LOW)

    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, GPIO.LOW)

    report_to_homeassistant(humidifier_entity_id, 'Off', humidifier_name, humidifier_icon)
    report_to_homeassistant(fan_entity_id, 'Off', fan_name, fan_icon)


def turn_on_humidifier():
    print('turning on humidifier')
    GPIO.output(button_pin, GPIO.HIGH)
    report_to_homeassistant(humidifier_entity_id, 'On', humidifier_name, humidifier_icon)

def turn_off_humidifier():
    print('turning off humidifier')
    GPIO.output(button_pin, GPIO.LOW)
    report_to_homeassistant(humidifier_entity_id, 'Off', humidifier_name, humidifier_icon)

def turn_on_fan():
    print('turning on fan')
    GPIO.output(fan_pin, GPIO.HIGH)
    report_to_homeassistant(fan_entity_id, 'On', fan_name, fan_icon)

def turn_off_fan():
    print('turning off fan')
    GPIO.output(fan_pin, GPIO.LOW)
    report_to_homeassistant(fan_entity_id, 'Off', fan_name, fan_icon)


def full_cycle():
    print('starting full cycle')
    global actively_using
    if actively_using:
        return
    
    usage_ended.clear()
    actively_using = True

    turn_on_fan()
    usage_ended.wait(roundDelaySec)

    for i in range(rounds):
        if not actively_using:
            break

        turn_on_humidifier()
        usage_ended.wait(roundLengthSec)

        turn_off_humidifier()
        usage_ended.wait(roundDelaySec)

    usage_ended.wait(roundLengthSec)
    turn_off_fan()
    actively_using = False
    print('completed full cycle')


def humidification_cycle():
    print('starting humidification cycle')
    global actively_using
    if actively_using:
        return

    usage_ended.clear()
    actively_using = True

    for i in range(rounds):
        if not actively_using:
            break

        turn_on_humidifier()
        usage_ended.wait(roundLengthSec)

        turn_off_humidifier()
        usage_ended.wait(roundDelaySec)

    turn_off_humidifier()
    actively_using = False
    print('humidification fan cycle')


def fan_cycle():
    print('starting fan cycle')
    global actively_using
    if actively_using:
        return
    
    usage_ended.clear()
    actively_using = True
    
    turn_on_fan()
    usage_ended.wait(roundLengthSec * rounds)

    turn_off_fan()
    actively_using = False
    print('completed fan cycle')


def turn_off():
    print('stopping current cycle')
    global actively_using
    actively_using = False

    usage_ended.set()
    turn_off_fan()
    turn_off_humidifier()


app = Flask(__name__)


@app.route('/')
def online():
    return 'OK'


@app.route('/fan/on')
def fan_on():
    Thread(target=fan_cycle).start()
    return 'On'

@app.route('/humidifier/on')
def humidifier_on():
    Thread(target=humidification_cycle).start()
    return 'On'

@app.route('/full/on')
def full_cycle_on():
    Thread(target=full_cycle).start()
    return 'On'


@app.route('/off')
def humidifier_off():
    turn_off()
    return 'Off'


if __name__ == '__main__':
    try:
        initialize()
        print('starting hosting')
        app.run(host='0.0.0.0')
    finally:
        GPIO.cleanup()
