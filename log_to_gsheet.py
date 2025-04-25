import base64
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import time

# Google Sheet setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1c2qwMEFSx_XwnN7sBb5mcEq1GGYYK_omxAtEW9o7VUc").worksheet("Sheet3")

# Google Drive setup
drive_service = build('drive', 'v3', credentials=creds)

def upload_media_to_drive(base64_data, file_name, folder_id):
    """
    Uploads a media file directly to Google Drive from base64 data and returns the file's URL.
    """
    # Decode the base64 string into binary data
    media_data = base64.b64decode(base64_data)

    # Create an in-memory file-like object from the binary data
    media_file = io.BytesIO(media_data)

    # Set the file metadata
    file_metadata = {
        'name': file_name,  # Name of the file in Google Drive
        'parents': [folder_id]  # Specify the folder ID
    }

    # Upload the file to Google Drive
    media = MediaIoBaseUpload(media_file, mimetype='application/octet-stream')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    # Get the URL of the uploaded file
    file_url = f'https://drive.google.com/file/d/{file_id}/view'
    return file_url

def process_logs_and_attachments():
    # Read output.txt
    with open(r"C:\Users\nikra\Documents\whatsapp-automation-bot\output.txt", "r", encoding='utf-8') as f:
        lines = f.readlines()

    # Google Drive folder ID for attachments
    folder_id = "1SIn4SMwQ-IvM5W1D-VnxgR5HbTIHa3tZ"

    # Filter and write logs
    for line in lines:
        if line.strip():  # Ignore blank lines
            # Check if the line contains a message with base64-encoded media
            if line.startswith("base64:"):
                # Extract the base64 string and file name
                base64_data = line[7:]  # Skipping the "base64:" part
                file_name = f"media_attachment_{int(time.time())}.jpg"  # You can modify this to dynamically extract file name based on logic

                # Upload media directly to Google Drive and get the file URL
                file_url = upload_media_to_drive(base64_data, file_name, folder_id)

                # Append the file URL to Google Sheets
                sheet.append_row([file_url])
            else:
                # If it's just a regular log (non-media), append it to the sheet
                sheet.append_row([line.strip()])

# Call the function to process logs and attachments
process_logs_and_attachments()
