from __future__ import print_function
import time
from sys import argv

from apiclient.discovery import build
from googleapiclient import sample_tools
from httplib2 import Http
from oauth2client import file, client, tools

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

DEBUG_ON = False

SCOPES = 'https://www.googleapis.com/auth/drive.file'
PDF_MIMETYPE = 'application/pdf'
FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
GDOCS_MIMETYPE = 'application/vnd.google-apps.document'
PHOTOBOOTH_ROOT = 'photobooth'

# sample test files
FILES = (
  ('hello.txt', None),
  ('hello.txt', GDOCS_MIMETYPE)
)

# authorization for GDrive API
def authorize_gdrive_api():
  print("\nconnecting to Google Drive API...")
  store = file.Storage('storage.json')
  creds = store.get()
  if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
    creds = tools.run_flow(flow, store, flags) \
      if flags else tools.run(flow, store)
  drive = build('drive', 'v3', http=creds.authorize(Http()))
  return drive 

def callback(request_id, response, exception):
  if exception:
    print(exception)
  else:
    if DEBUG_ON:
      print("Permission Id: %s" % response.get('id'))

# shareable to everyone
def make_gdrive_shareable(drive, folder_id):
  batch = drive.new_batch_http_request(callback=callback)
  user_permission = {
    'type': 'anyone',
    'role': 'reader',
  }

  batch.add(drive.permissions().create(
    fileId=folder_id,
    body=user_permission,
    fields='id'
  ))
  domain_permission = {
  'type': 'anyone',
  'role': 'reader',
  }
  batch.add(drive.permissions().create(
    fileId=folder_id,
    body=domain_permission,
    fields='id'
  ))
  batch.execute()

# create new gdrive folder with unique name and photobooth root (pbr)
def create_new_gdrive_folder(drive):
  # get the photobooth root folder id, or create one if it doesn't exist
  pbr_id = None
  list_query = "mimeType='%s' and trashed=false" % FOLDER_MIMETYPE
  file_list = drive.files().list(q=list_query).execute()['files']
  for file1 in file_list:
    if file1['name'] == PHOTOBOOTH_ROOT:
      pbr_id = file1['id']
  if not pbr_id:
    pbr_metadata = {
      'name': "photobooth",
      'mimeType' : FOLDER_MIMETYPE
    }
    pbr_id = drive.files().create(body=pbr_metadata, fields='id').execute()['id']

  # create unique subfolder for photos
  folder_name = "photobooth-" + str(int(time.time()))
  file_metadata = {
    'name' : folder_name,
    'parents' : [ pbr_id ],
    'mimeType' : FOLDER_MIMETYPE
  }
  return drive.files().create(body=file_metadata, fields='webViewLink, id').execute()

# use Google API to shorten long url to google drive for user convenience
def shorten_url(link):
  service, flags = sample_tools.init(
    argv, 'urlshortener', 'v1',__doc__,__file__, 
    scope='https://www.googleapis.com/auth/urlshortener')
  try:
    url = service.url()

    #Create a shortened URL by inserting the URL into the url collection
    body = {'longUrl': link}
    resp = url.insert(body=body).execute()
    short_url = resp['id']
  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize')
  return short_url

# upload the files (and convert if necessary)
def upload_files_to_gdrive(drive, files=FILES):
  folder = create_new_gdrive_folder(drive)
  folder_id = folder.get('id')
  folder_link = folder.get('webViewLink')
  if DEBUG_ON:
    print("files to upload:\n %s" % photo_files)
  shortened_link = shorten_url(folder_link)
  make_gdrive_shareable(drive, folder_id)
  print("\nshareable folder link: %s\n" % shortened_link)
  print("uploading photos..")
  for filename, mimeType in files:
    metadata = {'name':filename, 'parents': [ folder_id ]}
    if mimeType:
      if DEBUG_ON:
        print(mimeType)
      metadata['mimeType'] = mimeType
    res = drive.files().create(body=metadata, media_body=filename).execute()
    if res:
      print('Uploaded "%s" (%s)' % (filename, res['mimeType']))
  # NOTE this just returns the most recent uploaded file
  return res

# TEST: standard order
'''
drive = authorize_gdrive_api()
res = upload_files_to_gdrive(drive)
'''
