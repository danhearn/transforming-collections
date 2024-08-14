#Adapted from prototype-scripts/LED_matrix/main.py that used a galactic unicorn LED matrix. 
#This script uses the picographics library with the Interstate75 LED matrix displays

import select
import sys
import _thread as thread
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_256X64
import time

# create an Interstate75 object and a graphics framebuffer to draw into
i75 = Interstate75(display=DISPLAY_INTERSTATE75_256X64) # 256x64 pixel display (may need to change)
graphics = i75.display

# start position for scrolling (off the side of the display)
scroll = float(-i75.width)

# original message to scroll
MESSAGE = "TANC - Ready to read..."

# pen colours to draw with
BLACK = graphics.create_pen(0, 0, 5)
WHITE = graphics.create_pen(255, 0, 0)

# function to check for new messages
def check_messages():
    global MESSAGE
    if select.select([sys.stdin], [], [], 0)[0]:
        new_message = sys.stdin.readline()
        print(new_message)
        return new_message.strip()
    return None

# function to continuously update the display
def display_loop():
    global MESSAGE, scroll
    while True:
        # determine the scroll position of the text
        width = graphics.measure_text(MESSAGE, 0)
        scroll += 1
        if scroll > width + i75.width:
            scroll = float(-i75.width)

        # clear the graphics object
        graphics.set_pen(BLACK)
        graphics.clear()

        # draw the text
        graphics.set_pen(WHITE)
        graphics.text(MESSAGE, round(0 - scroll), 2, -1, 0.55)

        # update the display
        i75.update()
        time.sleep(0.02)

# function to run the main loop
def main_loop():
    global MESSAGE
    while True:
        new_message = check_messages()
        if new_message:
            MESSAGE = new_message
        
        # Add a small delay to avoid high CPU usage
        time.sleep(0.1)

# start the display loop in a separate thread
thread.start_new_thread(display_loop, ())

# run the main loop in the main thread
main_loop()
