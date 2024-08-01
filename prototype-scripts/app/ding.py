#<----------- IMPORTS & VARIABLES ------------>
import RPi.GPIO as GPIO
import pandas as pd
import numpy as np
from time import sleep
import json
import random
import mido 
from mido import MidiFile
from adafruit_servokit import ServoKit
from ast import literal_eval

#connected to test data
#df = pd.read_csv('../data/ding_tate_sea_overlay_reference.csv')
#df = pd.read_csv('app/data/tanc-etan_system-dataset.csv')

#turn strings of lists into strings
#df['Countries'] = df['Countries'].apply(lambda x: literal_eval(x) if pd.notnull(x) else x)

#country_track references stored in JSON file
#Midi files are stored in midi
with open('app/data/ding/country_tracks.json') as json_file:
    country_tracks = json.load(json_file)

#servokit setup
servo_kit = ServoKit(channels=16)
sleep(1)

#<----------- GPIO NUMBERS ---------------->
# GPIOs 2 & 3 reserved for servo driver
# PINS - to - reserved for LED matrix - need to figure this out. If communicating with another board that drives the matrix 8 & 10 will need to be reserved

#---- 8 bank Relay ----
#Anklung
ank1 = 4
ank2 = 14
ank3 = 15
ank4 = 18

#Gamelan
gamelan1 = 17
gamelan2 = 27
gamelan3 = 22
gamelan4 = 23

#---- 4 bank relay ----
#Tick Tock
tick1 = 10
tick2 = 9

#Drum
drum1 = 25
drum2 = 8

#<---------- SERVO CHANNELS ---------->

bells = 0
cymbal = 1
cowbell = 2
gong = 3
bells2 = 4

channels =[0,1,2,3,4]
#<----------- SETUP ------------>
GPIO.setmode(GPIO.BCM) #SETUP AS GPIO NUMBERS NOT PIN NUMBERS!
GPIO.setup(ank1, GPIO.OUT)
GPIO.setup(ank2, GPIO.OUT)
GPIO.setup(ank3, GPIO.OUT)
GPIO.setup(ank4, GPIO.OUT)
GPIO.setup(gamelan1,GPIO.OUT)
GPIO.setup(gamelan2,GPIO.OUT)
GPIO.setup(gamelan3,GPIO.OUT)
GPIO.setup(gamelan4,GPIO.OUT)
GPIO.setup(tick1, GPIO.OUT)
GPIO.setup(tick2, GPIO.OUT)
GPIO.setup(drum1, GPIO.OUT)
GPIO.setup(drum2, GPIO.OUT)

#Set all servos to position 0
for i in channels:
   servo_kit.servo[i].angle = 180

#<----------- INSTRUMENT FUNCTIONALITY ------------>
#solenoid functionality - turns on and off when msg = note_on from midi file
def solenoid(pin):
    #print(f"solenoid - pin: {pin}") # for debugging
    GPIO.output(pin, GPIO.HIGH)
    sleep(0.1)
    GPIO.output(pin, GPIO.LOW)

#servo functionality
def servo(channel, angle):
    #print(f"servo - channel: {channel}") # for debugging
    servo_kit.servo[channel].angle = angle
    sleep(0.2)
    servo_kit.servo[channel].angle = 180

#Play track reads the midi track and then listens for note_on or note_off.
#each output is assigned to a specific note value and will trigger one of the instrument functions
def playTrack(midiTrack):
    print("PLAY!")
    for msg in midiTrack.play():
        #print(msg)
        if msg.type == 'note_on':
            #print('note on!!')
            if msg.note == 60: # C3
                solenoid(ank1)
            elif msg.note == 61: # C#3
                solenoid(ank2)
            elif msg.note == 62: # D3
                solenoid(ank3)
            elif msg.note == 63: # D#3
                solenoid(ank4)
            elif msg.note == 64: # E3
                servo(bells,90)
                print('bells')
            elif msg.note == 65: # F3
                solenoid(tick1)
            elif msg.note == 66: # F#3
                solenoid(tick2)
            elif msg.note == 67: # G3
                servo(cymbal, 50)
                print('cymbal')
            elif msg.note == 68: # G#3
                servo(cowbell, 45)
                print('cowbell (cowgong)')
            elif msg.note == 69: # A3
                solenoid(gamelan1)
            elif msg.note == 70: # A#3
                solenoid(gamelan2)
            elif msg.note == 71: # B3
                solenoid(gamelan3) 
            elif msg.note == 72: # C4
                solenoid(gamelan4)
            elif msg.note == 73: # C#4
                solenoid(drum1)
            elif msg.note == 74: # D4
                solenoid(drum2)
            elif msg.note == 75: # D#4
                servo(gong, 30)
                print("gong")
            elif msg.note == 76:
                servo(bells2, 10)
                print("bells2(big ones)")


def selector(country, numberOfTracks): #Takes the country and randomly selects which track to play if more than 1 track
    if numberOfTracks == 2:
        r = random.random()
        if r < 0.5:
            playTrack(MidiFile(country_tracks[f'{country}']['track1']))
            print(f'{country}, track 1')
        else:
            playTrack(MidiFile(country_tracks[f'{country}']['track2']))
            print(f'{country}, track 2')
    else: 
        playTrack(MidiFile(country_tracks[f'{country}']['track1'])),
        print(f'{country}, track 1')

#<----------- 'DING' MODEL READER ------------>
def playDing(row):
    for i in row['Countries']:
        print(f"Processing country: {i}")
        #Countries with 2 tracks
        if i.lower() == "malaysia" or i.lower() == "vietnam" or i.lower() == "singapore" or i.lower() == "indonesia" or i.lower() == "thailand":
            selector(i.lower(), 2)
        #Countries with 1 track
        elif i.lower() == "myanmar" or i.lower() == "cambodia" or i.lower() == "laos" or i.lower() =="philippines":
            selector(i.lower(), 1)
        #LOW APPEARANCE INDEXES LAOS, BRUNEI, EAST-TIMOR
        else: 
            selector("no-country", 1)