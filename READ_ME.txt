This is a fork from safay/RPi_photobooth that adds Google Drive v3 API support so that sets of images are uploaded automatically after being taken, to a unique shareable folder with read permissions set to 'all'. Guests can then download the photos directly to their phones (or other devices) via a link.

To use the Google Drive API, you'll need to first generate an OAuth 2.0 client ID (Type: Other) from developers.google.com - and save it as client_secret.json in this project's root directory. When photo_booth.py is run, it will create a new folder called photobooth in your (the authenticating google user's) Google Drive root directory and a unique subfolder for each set of photos taken.

Google Drive and URL shortener services must be enabled from https://console.developers.google.com/apis 
