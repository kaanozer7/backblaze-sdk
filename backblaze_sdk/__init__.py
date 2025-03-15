import os
import requests
import hashlib
import urllib.parse
from dotenv import load_dotenv
from b2sdk.v2 import InMemoryAccountInfo, B2Api

# Load environment variables
load_dotenv()

# Backblaze B2 Credentials
B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APP_KEY = os.getenv("B2_APP_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

### Authentication ###
def get_b2_api():
    """
    Authenticate and return a B2Api instance.
    """
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
    return b2_api

### Upload Video Function ###
def upload_video(match_id, file_path, file_name):
    """
    Uploads a video file to Backblaze B2.
    """
    full_file_name = f"{match_id}/{file_name}"
    try:
        b2_api = get_b2_api()
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        bucket_id = bucket.id_
        response = b2_api.session.get_upload_url(bucket_id)
        upload_url = response['uploadUrl']
        auth_token = response['authorizationToken']
        
        with open(file_path, "rb") as file:
            file_data = file.read()
        sha1_hash = hashlib.sha1(file_data).hexdigest()
        encoded_file_name = urllib.parse.quote(full_file_name)
        
        headers = {
            "Authorization": auth_token,
            "X-Bz-File-Name": encoded_file_name,
            "Content-Type": "video/mp4",
            "X-Bz-Content-Sha1": sha1_hash,
        }
        
        upload_response = requests.post(upload_url, headers=headers, data=file_data)
        upload_response.raise_for_status()
        
        final_video_url = f"https://f002.backblazeb2.com/file/{B2_BUCKET_NAME}/{full_file_name}"

        return {
            "upload_url": upload_url,
            "auth_token": auth_token,
            "file_name": full_file_name,
            "final_video_url": final_video_url,
            "upload_response": upload_response.json(),
            "status": "success"
            }
    except Exception as e:
        return {"error": str(e)}

### Upload JSON Function ###
def upload_json(match_id, file_path, file_name):
    """
    Uploads a JSON file to Backblaze B2.
    """
    full_file_name = f"{match_id}/{file_name}"
    try:
        b2_api = get_b2_api()
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        bucket_id = bucket.id_
        response = b2_api.session.get_upload_url(bucket_id)
        upload_url = response['uploadUrl']
        auth_token = response['authorizationToken']
        
        with open(file_path, "rb") as file:
            file_data = file.read()
        sha1_hash = hashlib.sha1(file_data).hexdigest()
        encoded_file_name = urllib.parse.quote(full_file_name)
        
        headers = {
            "Authorization": auth_token,
            "X-Bz-File-Name": encoded_file_name,
            "Content-Type": "application/json",
            "X-Bz-Content-Sha1": sha1_hash,
        }
        
        upload_response = requests.post(upload_url, headers=headers, data=file_data)
        upload_response.raise_for_status()
          
        final_file_url = f"https://f002.backblazeb2.com/file/{B2_BUCKET_NAME}/{full_file_name}"
        
        return {
            "upload_url": upload_url,
            "auth_token": auth_token,
            "file_name": full_file_name,
            "final_file_url": final_file_url,
            "upload_response": upload_response.json()
        }

    
    except Exception as e:
        return {"error": str(e)}

### Download Function ###
def download_file(folder, file_name, local_path="downloaded_file"):
    """
    Downloads a file from Backblaze B2.
    """
    full_file_name = f"{folder}/{file_name}"
    try:
        b2_api = get_b2_api()
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        file = bucket.download_file_by_name(full_file_name)
        with open(local_path, "wb") as f:
            for chunk in file.response.iter_content(chunk_size=8192):
                f.write(chunk)
        return {"status": "success", "local_path": local_path}
    except Exception as e:
        return {"error": str(e)}

### File Viewer Function ###
def list_files(folder=None, recursive=False):
    """
    Lists all files in the Backblaze B2 bucket, optionally filtering by folder.
    """
    try:
        b2_api = get_b2_api()
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        file_list = []

        if recursive:
            # List all files recursively.
            for file_version, folder_name in bucket.ls(latest_only=True, recursive=True):
                if folder:
                    # If a folder is specified, filter to include only files that start with "folder/"
                    if file_version.file_name.startswith(f"{folder}/"):
                        file_list.append({
                            "file_name": file_version.file_name,
                            "upload_timestamp": file_version.upload_timestamp,
                            "folder": folder_name
                        })
                else:
                    file_list.append({
                        "file_name": file_version.file_name,
                        "upload_timestamp": file_version.upload_timestamp,
                        "folder": folder_name
                    })
        else:
            # Non-recursive listing: use folder_to_list if a folder is provided.
            if folder:
                iterator = bucket.ls(latest_only=True, folder_to_list=folder)
            else:
                iterator = bucket.ls(latest_only=True)
            for file_version, folder_name in iterator:
                file_list.append({
                    "file_name": file_version.file_name,
                    "upload_timestamp": file_version.upload_timestamp,
                    "folder": folder_name
                })

        return {"files": file_list}
    except Exception as e:
        return {"error": str(e)}
