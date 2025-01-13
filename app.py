"""""
from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)

# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = 'weezappstorage'  # Replace with your container name

# Function to check if the metadata file exists in Azure Blob Storage
def check_metadata_exists(file_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Check if the blob exists in the container
    blob_client = container_client.get_blob_client(file_name)
    return blob_client.exists()  # Returns True if the blob exists, False otherwise

# API Endpoint to check if metadata exists
@app.route('/check-metadata', methods=['POST'])
def check_metadata():
    data = request.get_json()
    file_name = data.get('fileName')

    if not file_name:
        return jsonify({'error': 'fileName is required'}), 400

    try:
        exists = check_metadata_exists(file_name)
        return jsonify({'exists': exists}), 200
    except Exception as e:
        print('Error checking metadata existence:', e)
        return jsonify({'error': 'Unable to check metadata existence.'}), 500

if __name__ == '__main__':
    app.run(port=6000)
"""
from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient, ContentSettings
import os
import base64
from io import BytesIO

app = Flask(__name__)

# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING_2 = os.getenv('AZURE_STORAGE_CONNECTION_STRING_1')
CONTAINER_NAME = 'weez-user-data'
METADATA_CONTAINER_NAME='weez-files-metadata'

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(os.getnev('AZURE_STORAGE_CONNECTION_STRING_1'))
container_client = blob_service_client.get_container_client(CONTAINER_NAME)
metadata_blob_service_client=BlobServiceClient.from_connection_string(os.getenv('AZURE_METADATA_STORAGE_CONNECTION_STRING'))
metadata_container_client=metadata_blob_service_client.get_container_client(METADATA_CONTAINER_NAME)

# Function to check if metadata exists in Azure Blob Storage
def check_metadata_exists(file_name, user_id):
    blob_client = metadata_container_client.get_blob_client(f"{user_id}/{file_name}.json")
    return blob_client.exists()

# Function to upload the file to Blob Storage if metadata does not exist
def upload_file_to_blob(file_data, file_name, user_id):
    """
    try:
        blob_client = container_client.get_blob_client(f"{user_id}/{file_name}.json")
        file_bytes = BytesIO(base64.b64decode(file_data))
        blob_client.upload_blob(file_bytes, overwrite=True, content_settings=ContentSettings(content_type="application/octet-stream"))
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False
        """
    #try:
    blob_client = container_client.get_blob_client(f"{user_id}/{file_name}")
    cleaned_data = file_data.replace(" ", "").replace("\n", "").replace("\r", "")

    # Fix padding for base64 data if necessary
    missing_padding = len(cleaned_data) % 4 #file_data
    if missing_padding:
            cleaned_data += '=' * (4 - missing_padding) #file_data
    try:
        # Decode the base64 string
        file_bytes = BytesIO(base64.b64decode(cleaned_data)) #file_data
    
        # Upload file to Azure Blob Storage
        blob_client.upload_blob(file_bytes, overwrite=True,blob_type="BlockBlob", content_settings=ContentSettings(content_type="application/octet-stream"))
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

# API Endpoint to check if metadata exists and upload if it doesn’t
@app.route('/check-metadata', methods=['POST'])
def check_metadata():
    data = request.get_json()
    user_id = data.get('userID')
    file_name = data.get('fileName')
    file_path = data.get('filePath')
    file_data =data.get('fileData')  # Assume this is the path to the file

    if not user_id or not file_name or not file_path:
        return jsonify({'error': 'userID, fileName, and filePath are required'}), 400

    try:
        # Check for existing metadata
        exists = check_metadata_exists(file_name, user_id)

        if exists:
            return jsonify({'exists': True}), 200
        else:
            # If metadata doesn't exist, upload the file
            upload_successful = upload_file_to_blob(file_data, file_name, user_id)
            if upload_successful:
                return jsonify({'exists': False, 'message': 'File uploaded successfully.'}), 201
            else:
                return jsonify({'exists': False, 'error': 'File upload failed.'}), 500
    except Exception as e:
        print('Error checking metadata existence or uploading file:', e)
        return jsonify({'error': 'Unable to check metadata existence or upload file.'}), 500

if __name__ == '__main__':
    app.run(port=8000)
