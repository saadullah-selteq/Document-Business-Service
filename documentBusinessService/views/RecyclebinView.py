from utils.util import containerClient

from utils.util import containerClient
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlobServiceClient
from core import secrets
import traceback
from rest_framework.views import APIView
from documentBusinessService import service
from documentBusinessService.models import *
from utils.responses import internal_server_error, ok
import datetime

import re
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from documentBusinessService.serializer.BusinessFileSerializer import BusinessFileSerializer
from documentBusinessService.serializer.BusinessSerializer import BusinessSerializer


def delete_virtual_directory(container_name, directory_path):
    container_client = containerClient()
    blobs = container_client.list_blobs(name_starts_with=directory_path)
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        blob_client.delete_blob()



def rename_virtual_directory(container_name, old_directory_name, new_directory_name):
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=secrets.AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)

    # Get the list of blobs in the old directory
    blob_list = container_client.list_blobs(name_starts_with=old_directory_name)
    container_client.upload_blob(name=new_directory_name, data=b'')
    # Copy each blob to the new directory
    try:
        for blob in blob_list:
            new_blob_name = new_directory_name + blob.name[len(old_directory_name):]
            blob_client = container_client.get_blob_client(new_blob_name)
            source_blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob.name}"
            blob_client.start_copy_from_url(source_blob_url)
            # Optional: Delete the old blob
            # container_client.delete_blob(blob.name)
        try:
            # Delete the old directory
            blobs = container_client.list_blobs(name_starts_with=old_directory_name)
            for blob in blobs:
                blob_client = container_client.get_blob_client(blob)
                blob_client.delete_blob()
        except Exception as err:
            return "failed to delete directory"
    except Exception as err:
        return "failed to duplicate directory"




class emptyrecyclebinbusiness(APIView):

    @swagger_auto_schema(
        operation_id='restore_data',
        operation_description='Restore deleted data.',
        manual_parameters=[
            openapi.Parameter(
                'ownerId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the owner of the data to be restored.',
                required=True
            ),
            openapi.Parameter(
                'type', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The type of data to be restored. Possible values: "all", "folder", "file".',
                required=True,
                enum=["all", "folder", "file"]
            ),
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to be restored. Required when type is "folder".'
            ),
            openapi.Parameter(
                'fileId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the file to be restored. Required when type is "file".'
            ),
        ]
    )
    def post(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            type = request.GET.get('type', None)
            if type == "all":
                DocumentBusinessFolder.objects.filter(ownerId=ownerId, isDeleted=True, permanentDelete=False).update(
                    isDeleted=False)
                DocumentBusinessFile.objects.filter(ownerId=ownerId, isDeleted=True, permanentDelete=False).update(
                    isDeleted=False)
                return ok(message="Successfull restore data")
            elif type == "folder":
                folderId = request.GET.get('folderId', None)
                DocumentBusinessFolder.objects.filter(folderId=folderId, isDeleted=True, permanentDelete=False).update(
                    isDeleted=False)
                DocumentBusinessFolder.objects.filter(folderParentId=folderId, isDeleted=True,
                                                      permanentDelete=False).update(isDeleted=False)
                DocumentBusinessFile.objects.filter(folderId=folderId, isDeleted=True, permanentDelete=False).update(
                    isDeleted=False)
                return ok(message="Successfull restore folder")
            elif type == "file":
                fileId = request.GET.get('fileId', None)
                DocumentBusinessFile.objects.filter(fileId=fileId, isDeleted=True, permanentDelete=False).update(
                    isDeleted=False)
                return ok(message="Successfull file restore")

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message=str(err))

    @swagger_auto_schema(
        operation_id='get_recycle_bin_data',
        operation_description='Get data from the recycle bin.',
        manual_parameters=[
            openapi.Parameter(
                'ownerId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the owner whose recycle bin data to retrieve.',
                required=True
            ),
        ]
    )
    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            if ownerId is not None:
                data = service.getRecycleBin(ownerId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get data')

    @swagger_auto_schema(
        operation_id='empty_recycle_bin',
        operation_description='Empty the recycle bin.',
        manual_parameters=[
            openapi.Parameter(
                'ownerId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the owner whose recycle bin to empty.',
                required=True
            ),
            openapi.Parameter(
                'businessId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the business to which the owner belongs.',
                required=True
            ),
            openapi.Parameter(
                'type', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The type of data to permanently delete. Values can be "all", "folder", or "file".',
                required=True
            ),
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to permanently delete (required if type is "folder").',
                required=False
            ),
            openapi.Parameter(
                'fileId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the file to permanently delete (required if type is "file").',
                required=False
            ),
        ]
    )
    def delete(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            businessId = request.GET.get('businessId', None)
            delete_datetime = datetime.datetime.now()
            type = request.GET.get('type', None)
            updatedAt = datetime.datetime.now()
            userStorage = Business.objects.get(businessId=businessId)
            serlizeData = BusinessSerializer(userStorage)
            remainingStorage = serlizeData.data['remainingStorage']
            match = re.search(r'\d+(\.\d+)?', remainingStorage)
            # Get the matched number as a float
            number = float(match.group())
            kb = number * 1000000
            if type == "all":
                files = DocumentBusinessFile.objects.filter(ownerId=ownerId, isDeleted=True, permanentDelete=False)
                fileSerilzer = BusinessFileSerializer(files, many=True)
                data = fileSerilzer.data
                total_size = sum(float(item['size']) for item in data)
                kb = kb + total_size
                gb = kb / 1000000
                print(gb)
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                storageserializer = BusinessSerializer(userStorage, data=storageData, partial=True)
                if storageserializer.is_valid(raise_exception=True):
                    storageserializer.save()
                    DocumentBusinessFolder.objects.filter(ownerId=ownerId, isDeleted=True,
                                                          permanantDelete=False).update(permanentDelete=True,
                                                                                        permanentDeletedOn=delete_datetime)
                    DocumentBusinessFile.objects.filter(ownerId=ownerId, isDeleted=True, permanentDelete=False).update(
                        permanentDelete=True, permanentDeletedOn=delete_datetime)
                    return ok(message='Successfully empty recycle bin')

            elif type == "folder":
                folderId = request.GET.get('folderId', None)
                files = DocumentBusinessFile.objects.filter(folderId=folderId, isDeleted=True)
                fileSerilzer = BusinessFileSerializer(files, many=True)
                data = fileSerilzer.data
                total_size = sum(float(item['size']) for item in data)
                kb = kb + total_size
                gb = kb / 1000000
                print(gb)
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                storageserializer = BusinessSerializer(userStorage, data=storageData, partial=True)
                if storageserializer.is_valid(raise_exception=True):
                    storageserializer.save()
                    DocumentBusinessFolder.objects.filter(folderId=folderId, isDeleted=True,
                                                          permanentDelete=False).update(permanentDelete=True,
                                                                                        permanentDeletedOn=delete_datetime)
                    DocumentBusinessFolder.objects.filter(folderParentId=folderId, isDeleted=True,
                                                          permanentDelete=False).update(permanentDelete=True,
                                                                                        permanentDeletedOn=delete_datetime)
                    DocumentBusinessFile.objects.filter(folderId=folderId, isDeleted=True,
                                                        permanentDelete=False).update(permanentDelete=True,
                                                                                      permanentDeletedOn=delete_datetime)
                    return ok(message='Successfully folder permanent delete')
            elif type == "file":
                fileId = request.GET.get('fileId', None)
                file = DocumentBusinessFile.objects.filter(fileId=fileId, isDeleted=True)
                fileSerilzer = BusinessFileSerializer(file, many=True)
                data = fileSerilzer.data
                print(data)
                kb = kb + float(data[0]['size'])
                gb = kb / 1000000
                print(gb)
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                storageserializer = BusinessSerializer(userStorage, data=storageData, partial=True)
                if storageserializer.is_valid(raise_exception=True):
                    storageserializer.save()
                    DocumentBusinessFile.objects.filter(fileId=fileId, isDeleted=True, permanentDelete=False).update(
                        permanentDelete=True, permanentDeletedOn=delete_datetime)
                    return ok(message='Successfully file permanent delete')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete file')
