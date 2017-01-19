Description
===========

This is a photo booth + Google Drive uploader for the Raspberry Pi. It is a fork from safay/RPi_photobooth that adds Google Drive v3 API support so that sets of images from each photobooth session are uploaded automatically after being taken, to a unique shareable folder with public read permissions. Guests can then easily download the full-quality photobooth session photos directly to their phones (or other devices) via a Google shortened link.

Hardware controller (optional), based on [this instructables guide](http://www.instructables.com/id/Raspberry-Pi-photo-booth-controller/)

Google API set-up
=================

To use the Google Drive API, you'll need to first generate an OAuth 2.0 client ID (Type: Other) from developers.google.com - and save it as client_secret.json in this project's root directory. When photo_booth.py is run, it will create a new folder called photobooth in your (the authenticating google user's) Google Drive root directory and a unique subfolder for each set of photos taken.

Google Drive and URL shortener services must be enabled from https://console.developers.google.com/apis 


To run
======

1. Generate client_secret.json (as described above) and place in RPi_photobooth
2. from terminal: pip install -r requirements.txt
3. ensure that gphoto2 is installed. Test from terminal: gphoto2 --capture-image-and-download
4. from terminal: python photo_booth.py
