#!/usr/bin/python

import RPi.GPIO as GPIO, time, os, subprocess
import time
import gdrive_loader as gdrive

# user variables
HARDWARE_DEBUG_ON = False
ENABLE_PRINTING = False
# set STANDARD_SWITCH_ON = True for inverted button/switch
SWITCH_DEFAULT_ON = False
PHOTO_MIMETYPE = None
# PHOTO_MIMETYPE = "application/vnd.google-apps.photo"

print("\nRaspberry Pi Photobooth - AleXXX edition\n")
print("Press Enter or the hardware 'start' button to begin")

# GPIO setup
GPIO.setwarnings(HARDWARE_DEBUG_ON)
GPIO.setmode(GPIO.BCM)
SWITCH = 24
GPIO.setup(SWITCH, GPIO.IN)
RESET = 25
GPIO.setup(RESET, GPIO.IN)
PRINT_LED = 22
POSE_LED = 18
BUTTON_LED = 23
GPIO.setup(POSE_LED, GPIO.OUT)
GPIO.setup(BUTTON_LED, GPIO.OUT)
GPIO.setup(PRINT_LED, GPIO.OUT)
GPIO.output(BUTTON_LED, True)
GPIO.output(PRINT_LED, False)

def run_photobooth():
  while True:
    if (not GPIO.input(SWITCH) == SWITCH_DEFAULT_ON or raw_input() != None):
      snap = 0
      photo_files =()
      while snap < 4:
        print("pose!")
        GPIO.output(BUTTON_LED, False)
        GPIO.output(POSE_LED, True)
        time.sleep(1.5)
        for i in range(5):
          GPIO.output(POSE_LED, False)
          time.sleep(0.4)
          GPIO.output(POSE_LED, True)
          time.sleep(0.4)
        for i in range(5):
          GPIO.output(POSE_LED, False)
          time.sleep(0.1)
          GPIO.output(POSE_LED, True)
          time.sleep(0.1)
        GPIO.output(POSE_LED, False)
        print("SNAP")

        #take photo and save with gphoto2
        photo_file = "/home/pi/photobooth_images/photobooth%d.jpg" % int(time.time())
        photo_files += ((photo_file,PHOTO_MIMETYPE),)
        gphoto2_capture_args = "gphoto2 --capture-image-and-download --filename  %s" % photo_file
        gpout = subprocess.check_output(gphoto2_capture_args, stderr=subprocess.STDOUT, shell=True)
        if HARDWARE_DEBUG_ON or "ERROR" in gpout:
          print(gpout)
        if "ERROR" not in gpout: 
          snap += 1
        GPIO.output(POSE_LED, False)
        time.sleep(0.5)

      # Google Drive uploading
      drive = gdrive.authorize_gdrive_api()
      gdrive.upload_files_to_gdrive(drive, photo_files)
      
      # original printer stuff.
      if ENABLE_PRINTING:
        print("please wait while your photos print...")
        GPIO.output(PRINT_LED, True)
        # build image and send to printer
        subprocess.call("sudo /home/pi/scripts/photobooth/assemble_and_print", shell=True)
        # TODO: implement a reboot button
        # Wait to ensure that print queue doesn't pile up
        # TODO: check status of printer instead of using this arbitrary wait time
        time.sleep(110)

      print("ready for next round")
      GPIO.output(PRINT_LED, False)
      GPIO.output(BUTTON_LED, True)

if __name__ == "__main__":
  run_photobooth()
