from utils.util import containerClient
from azure.storage.blob import ContentSettings


def upload_file_to_azure_storage(file, ownerId, virtual_directory):
    blob_service_client = containerClient()

    # Set the name of the blob (file) that will be uploaded
    blob_name = ownerId + "/" + virtual_directory + file.name

    # Set the content type of the file (optional)
    content_settings = ContentSettings(content_type=file.content_type)
    requestType = 'BlockBlob'

    # Upload the file to Azure Storage
    block_blob_service = blob_service_client.get_blob_client(blob=blob_name)
    block_blob_service.upload_blob(file, blob_type=requestType, content_settings=content_settings)
    blob_properties = block_blob_service.get_blob_properties()
    file_url = block_blob_service.url
    file_size = blob_properties.size
    file_type = content_settings.content_type
    # Return the URL of the uploaded file
    return {'url': file_url, 'size': file_size / 1000000.0, 'type': file_type}
