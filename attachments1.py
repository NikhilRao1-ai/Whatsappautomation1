import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API setup
scope_drive = ['https://www.googleapis.com/auth/drive']
creds_drive = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope_drive)
drive_service = build('drive', 'v3', credentials=creds_drive)

# Google Sheets API setup
scope_sheets = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds_sheets = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope_sheets)
client = gspread.authorize(creds_sheets)
sheet = client.open_by_key("1c2qwMEFSx_XwnN7sBb5mcEq1GGYYK_omxAtEW9o7VUc").worksheet("Sheet3")

# Google Drive folder ID where you want to upload attachments
google_drive_folder_id = '1SIn4SMwQ-IvM5W1D-VnxgR5HbTIHa3tZ'

# Check if the folder exists before uploading
def check_folder_exists(folder_id):
    try:
        folder = drive_service.files().get(fileId=folder_id).execute()
        print(f"Folder found: {folder['name']}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Upload file to Google Drive folder
def upload_to_drive(file_path, file_name):
    try:
        # Create a media object for the file
        media = MediaFileUpload(file_path, mimetype='image/jpeg', resumable=True)

        # Upload the file to Google Drive
        request = drive_service.files().create(
            media_body=media,
            body={
                'name': file_name,
                'parents': [google_drive_folder_id]
            }
        )

        # Execute the upload request
        file = request.execute()
        print(f"File uploaded successfully: {file['name']}")
    except Exception as e:
        print(f"Error uploading file {file_name}: {e}")

# Read output.txt and upload data to Google Sheets
with open(r"C:\Users\nikra\Documents\whatsapp-automation-bot\output.txt", "r", encoding='utf-8') as f:
    lines = f.readlines()

# Filter and write logs to Google Sheets
for line in lines:
    if line.strip():  # ignore blank lines
        sheet.append_row([line.strip()])

# Get the list of files in the 'downloads' folder to upload attachments
downloads_folder = r"C:\Users\nikra\Documents\whatsapp-automation-bot\downloads"

# Ensure the folder exists
if os.path.exists(downloads_folder):
    # Check if the folder exists on Google Drive before uploading
    if check_folder_exists(google_drive_folder_id):
        # Iterate over files in the 'downloads' folder and upload them
        for filename in os.listdir(downloads_folder):
            file_path = os.path.join(downloads_folder, filename)

            if os.path.isfile(file_path):
                # Upload the file
                upload_to_drive(file_path, filename)
                # Optionally, remove the file after upload
                os.remove(file_path)
                print(f"File {filename} uploaded and deleted.")
    else:
        print(f"Folder with ID {google_drive_folder_id} does not exist.")
else:
    print(f"Downloads folder {downloads_folder} does not exist.")
