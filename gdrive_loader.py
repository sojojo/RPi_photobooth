from __future__ import print_function
import os
import time

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

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
  store = file.Storage('storage.json')
  creds = store.get()
  if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store, flags) \
      if flags else tools.run(flow, store)
  drive = build('drive', 'v3', http=creds.authorize(Http()))
  return drive 

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
  return drive.files().create(body=file_metadata, fields='id').execute()


# upload the files (and convert if necessary)
def upload_files_to_gdrive(drive, files=FILES):
  folder = create_new_gdrive_folder(drive)
  folder_id = folder.get('id')
  for filename, mimeType in files:
    metadata = {'name':filename, 'parents': [ folder_id ]}
    if mimeType:
      metadata['mimeType'] = mimeType
    res = drive.files().create(body=metadata, media_body=filename).execute()
    if res:
      print('Uploaded "%s" (%s)' % (filename, res['mimeType']))
  # NOTE this just returns the most recent uploaded file
  return res

# on successful upload
def download_pdf_from_gdrive(res):
  if res:
    data = drive.files().export(fileId=res['id'], mimeType=PDF_MIMETYPE).execute()
    if data:
      # grab filename without extension
      fn = '%s.pdf' % os.path.splitext(filename)[0]
      # write text (binary) to local directory as pdf
      with open(fn, 'wb') as fh:
        fh.write(data)
      print('Downloaded "%s" (%s)' % (fn, PDF_MIMETYPE))

# TEST: standard order
drive = authorize_gdrive_api()
res = upload_files_to_gdrive(drive)
# download_pdf_from_gdrive(res)
