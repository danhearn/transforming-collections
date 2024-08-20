@ -1,77 +0,0 @@
#this file is a copy of the file stored on the Raspberry Pi Pico W that controls the Galactic Unicorn LED Matrix
#To upload any changes you will need to connect the Galactic Unicorn to the TANC raspberry Pi 4 and open Thonny where you will find the files saved to the pico
#Copy and paste any changes and save it to main.py as this is the file that runs by default 
# peace and love - DAN HEARN 4/1/24

#FOR REFERENCE ONLY:
import select
import sys
import _thread as thread
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN
import time

# create a PicoGraphics framebuffer to draw into
graphics = PicoGraphics(display=DISPLAY_GALACTIC_UNICORN)

# create our GalacticUnicorn object
gu = GalacticUnicorn()

# start position for scrolling (off the side of the display)
scroll = float(-GalacticUnicorn.WIDTH)

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
        if scroll > width + GalacticUnicorn.WIDTH:
            scroll = float(-GalacticUnicorn.WIDTH)

        # clear the graphics object
        graphics.set_pen(BLACK)
        graphics.clear()

        # draw the text
        graphics.set_pen(WHITE)
        graphics.text(MESSAGE, round(0 - scroll), 2, -1, 0.55)

        # update the display
        gu.update(graphics)
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
