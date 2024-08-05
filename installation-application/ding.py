import random
import json 
from mido import MidiFile

class DingModel:
    def __init__(self, arduino, json_path):
        self.arduino = arduino
        with open(json_path) as json_file:
            self.country_tracks = json.load(json_file)
    
    def read_midi(self, midi_file):
        for msg in midi_file.play():
            if msg.type == 'note_on':
                if msg.note >= 60 or msg.note <= 79: # C3 to G4
                    self.arduino.send_serial(msg.note - 42)
    
    def track_selector(self, country, num_of_tracks):
        if num_of_tracks == 2:
            r = random.random()
            if r < 0.5:
                self.read_midi(MidiFile(self.country_tracks[f'{country}']['track1']))
            else:
                self.read_midi(MidiFile(self.country_tracks[f'{country}']['track2']))
        else:
            self.read_midi(MidiFile(self.country_tracks[f'{country}']['track1']))
    
    def run(self, countries):
        for i in countries:
            if i == "Malaysia" or i == "Vietnam" or i == "Singapore" or i == "Indonesia" or i == "Thailand":
                self.track_selector(i.lower(), 2)
            elif i == "Myanmar" or i == "Cambodia" or i == "Laos" or i =="Philippines":
                self.track_selector(i.lower(), 1)
            else: 
                self.track_selector("no-country", 1)