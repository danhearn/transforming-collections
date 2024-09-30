# Ancestral (R)evocations - Installation Instructions 

These instructions are for running the installation only. They do not cover installation set-up.

Technical contact: 
**Dan Hearn - 07557648062** 

**Contents: **

1. Startup 
2. Screen Setup
3. Shutdown
4. Troubleshooting

## 1. Startup 

First ensure that the system is powered, there are 4 powered elements:
- 12v Solenoid power (mac mini stand)
- Small Screen power (mac mini stand)
- Mac Mini power (mac mini stand)
- Large LED Matrix (LED Matrix stand)

**To start the installation hold down the power button situated on the top-right corner of the Mac Mini until you hear the Mac startup sound.** 

The Mac will initialise the installation program automatically within around 30 seconds of power on. 

It will then proceed to play a test program for approximately 2 minuets, which triggers each instrument and displays `"Reading data..."` on both LED screens. During this time there are a number of elements you should check to ensure the installation is running correctly:

- Check all instruments are being triggered 
- Check both LED Screens are displaying `"Reading data.."` 

If there are problems see **section 4 troubleshooting**, or restart the system.

After the test program is complete the main installation program will begin automatically. **It is strongly advised that you restart the installation by following the shutdown process, as there can be issues on first startup with the Arduino that controls the instruments.** This will also give a second opportunity to check the functioning of the instruments. 

## 2. Screen Setup

Once the installation is up and running, you will need to position the video and terminal window onto the respective screen. 
Using the mouse provided:

1. move the video window onto the large TV screen by dragging it off to the right of the small screen situated above the Mac Mini
2. Maximise the video window by clicking the green dot at the top left corner of the window. 
3. On the small screen maximise the terminal window by clicking the green dot at the top left corner of the window.
4. Move the mouse cursor to the corner of the screen so it is not visible. 

Each screens should look like this: 
<img src="">
<img src="">

## 3. Shutdown 

To shutdown the system hold down the power button situated on the top right of the mac mini until the screens turn black. This may take around 20 seconds. 

## 4. Troubleshooting 

### General trouble shooting flow
- Check power supplies
- Check connections 
- Restart the Mac Mini 
- If issues persist contact Dan Hearn or Erika Tan

### Single instrument not triggering 
This will likely be determined on startup, and will be a mechanical or wiring issue.

- Check the instrument solenoid moves freely by gently moving it with your hand. If it does not move then this is likely the issue - contact Dan Hearn and proceed without instrument by disconnecting it.
- Replace the power cable between instrument and "the brain". If this does not fix the issue contact Dan Hearn and proceed without instrument by disconnecting it. 

### Damaged instrument 
Disconnect the instrument and report to Dan Hearn or Erika Tan.

### All instruments not triggering
This is likely a software issue. 

There are some programmed pauses in the instruments that last for around 2 minutes and occur every 10-15 minutes. **If you notice the instruments have not played for longer than 5 minutes, then there is an issue with the program and it must be restarted.** This is a known problem but rarely occurs, this is why it is recommended the installation is restarted after the initial startup sequence. 

Check the instruments are powered. The 12v plug should display a small green light when operating normally. 

Check the small screen for any error messages.

If the instruments do not trigger after restart call Dan Hearn immediately. 

### Large screen does not connect

- Check the HDMI connections 
- Check the mac mini display settings - 2 screens should be listed

If only 1 screen is listed, replace the HDMI cable or USB-C splitter from the Mac Mini. Try restarting the mac mini. 

### Large screen is mirroring small screen 

- Go to system settings>display 
- Select the large screen 
- Select use as separate display

### Mac Mini Audio is not playing 
Check volume is full on the mac mini. Check aux connection to audio system. 

If all fine then follow these steps or contact Dan Hearn:
- In applications open `pd-0.55` (pure data). 
- Once open go to settings>audio. 
- Check that output device is set to headphones.
- Click save preferences.
- Restart the mac mini.

### Large LED display not working 
if the large LED display is displaying `"TANC - Ready to read..."` Then there is a communication issue between it and mac mini. Check the USB connection. Restart the mac mini. 

If the large LED is displaying `"Reading Data..."` while the small LED is displaying other text - restart the mac mini. 

If the large LED is blank or 'glitchy' check the power supply to the screen.

If any issues persist then contact Dan Hearn.
