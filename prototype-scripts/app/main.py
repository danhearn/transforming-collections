import pandas as pd
import numpy as np
from ast import literal_eval
import ding
import semantic
import text 
import random
import video
import os
from time import sleep
from pythonosc import udp_client

#import dataset
df = pd.read_csv('data/input/tanc-etan_system-dataset.csv')
df['Countries'] = df['Countries'].apply(lambda x: literal_eval(x) if pd.notnull(x) else x)

df['Vectors'] = semantic.make_vectors(4)

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

#start playing sound

#check the galactic unicorn (LED Matrix) is connected
serial_connected = False
if os.path.exists('/dev/ttyACM0') == True:   #to list other devices use this command in the terminal: ls /dev/tty.*

    import serial
    ser = serial.Serial('/dev/ttyACM0', 9600)
    serial_connected = True
    print('Unicorn detected - ready to print text') #for debugging
    sleep(0.5)
else:
    print('Unicorn was not detected - LED Matrix Not Available') #for debugging

def testDing():
    all_countries = ['malaysia', 'vietnam', 'myanmar', 'laos', 'thailand', 'cambodia', 'indonesia', 'east-timor', 'philippines', 'singapore', 'brunei']
    for country in all_countries:
        ding.playDing({'Countries': [country]})
        sleep(2)
testDing()
### MODEL
while True:
    random_index = random.randint(0, len(df) - 1)
    row = df.iloc[random_index]
    print(f"Processing index: {random_index}, Countries: {row['Countries']}, Keywords: {row['Keywords']}, Label and vectors: {[row['Label']] +  list(row['Vectors'])}")
    #Display keywords while ding plays
    if pd.notnull(row['Keywords']) and serial_connected:
        try:
            #text.displayText(row) << need to put the code below into text.py???
            text = str(row['Keywords']) +'\n'
            ser.write(bytes(text.encode('ascii')))
            sleep(0.5)
        except serial.SerialException as e:
            print('Serial port Error:', e)
            pass
        except Exception as e:
            print('serial not working')
            pass

    #SEMANTIC
    #vectors = [float(value) for value in row['Vectors']]
    #client.send_message("/vectors", [row['Label']] +  vectors)

    #Ding model
    if isinstance(row['Countries'], list) and len(row['Countries']) > 0:
        ding.playDing(row)