import os
import io
import time
import base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials

# Google Drive API setup
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
drive_service = build('drive', 'v3', credentials=creds)

# Folder IDs
TEACHER_FOLDER_ID = '1MZFbfx-HW6OFoccjgSmgC8lSJUoFYOBr'
IT_FOLDER_ID = '1Lhyc1yycJ0lUbjYyCTqzsyrtKIvL30MK'
GENERAL_FOLDER_ID = '1QPwPjNJtXkfkouDmNI0OuzHlKsh4j5Pe'

# Keywords
TEACHER_KEYWORDS = ['teacher', 'pgt', 'tgt', 'school', 'faculty', 'principal', 'educator', 'academic']
IT_KEYWORDS = ['developer', 'software', 'engineer', 'programmer', 'it', 'python', 'java', 'cloud', 'node', 'tech', 'fullstack', 'backend', 'frontend', 'devops']

# Allowed file types
ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']

# Download folder path
DOWNLOADS_FOLDER = os.path.join(os.getcwd(), 'downloads')

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().lower()
    except Exception:
        return ""

def classify_resume(file_path):
    """Determine resume category based on keywords in content."""
    content = read_file_content(file_path)
    if any(keyword in content for keyword in TEACHER_KEYWORDS):
        return TEACHER_FOLDER_ID
    elif any(keyword in content for keyword in IT_KEYWORDS):
        return IT_FOLDER_ID
    else:
        return GENERAL_FOLDER_ID

def upload_to_drive(file_path, file_name, folder_id):
    try:
        media = MediaFileUpload(file_path, resumable=True)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"✅ Uploaded {file_name} to folder {folder_id}")
        return True
    except Exception as e:
        print(f"❌ Error uploading {file_name}: {e}")
        return False

def process_and_upload_resumes():
    if not os.path.exists(DOWNLOADS_FOLDER):
        print("❌ Downloads folder not found.")
        return

    for file_name in os.listdir(DOWNLOADS_FOLDER):
        file_path = os.path.join(DOWNLOADS_FOLDER, file_name)
        ext = os.path.splitext(file_name)[1].lower()

        if not os.path.isfile(file_path):
            continue

        # Delete unsupported files
        if ext not in ALLOWED_EXTENSIONS:
            print(f"⚠️ Skipping non-resume file: {file_name}")
            os.remove(file_path)
            print(f"🗑️ Deleted non-resume file: {file_name}")
            continue

        # Classify and upload
        target_folder = classify_resume(file_path)
        if upload_to_drive(file_path, file_name, target_folder):
            os.remove(file_path)
            print(f"🗑️ Deleted local file: {file_name}")

# Run the script
if __name__ == "__main__":
    process_and_upload_resumes()
