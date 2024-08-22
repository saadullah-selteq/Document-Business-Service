from documentBusinessService.models import *
import traceback
import datetime
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from azure.core.exceptions import ResourceExistsError
from documentBusinessService import service
from documentBusinessService.serializer.BusinessFolderSerializer import BusinessFolderSerializer
from documentBusinessService.models import DocumentBusinessFolder, DocumentBusinessFile
from utils.responses import conflict, internal_server_error, bad_request, created, ok
from utils.util import containerClient


class SingleFile(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'fileId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the file to retrieve.',
                required=True
            ),
        ],
        operation_id='get_single_file',
        operation_description='Retrieve a single file by its ID.'
    )
    def get(self, request):
        fileId = request.GET.get('fileId')
        if not fileId:
            return bad_request(message='File ID is required')
        data = service.getSignleFile(fileId)
        return ok(data=data)


class UploadBusinessFiles(APIView):
    @swagger_auto_schema(
        operation_id='upload_file',
        operation_description='Upload a file to the specified folder.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['requestType', 'filePath', 'ownerId', 'folderId', 'myFile'],
            properties={
                'requestType': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Type of the request.'
                ),
                'filePath': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Path of the file to be uploaded.'
                ),
                'ownerId': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='ID of the owner (business).'
                ),
                'folderId': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='ID of the folder where the file will be uploaded.'
                ),
                'myFile': openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description='The file to be uploaded.'
                )
            }
        ))
    def post(self, request):
        request_data = request.data
        requestType = request_data.get('requestType')
        filePath = request_data.get('filePath')
        ownerId = request_data.get('ownerId')
        folderId = request_data.get('folderId')
        file = request.FILES['myFile']
        file_name = file.name
        updatedAt = datetime.datetime.now()

        businessStorage = Business.objects.get(businessId=ownerId)
        serlizeData = BusinessSerializer(businessStorage)
        remainingStorage = serlizeData.data['remainingStorage']
        match = re.search(r'\d+(\.\d+)?', remainingStorage)
        number = float(match.group())
        kb = number * 1000000

        data = upload_file_to_azure_storage(file, ownerId, filePath, requestType)
        request_data['size'] = data['size']
        request_data['type'] = data['type']
        request_data['fileUrl'] = data['url']
        request_data['fileName'] = file_name
        folder_obj = DocumentBusinessFolder.objects.get(folderId=folderId)
        request_data['folderId'] = folder_obj.folderId
        kb -= data['size']
        gb = kb / 1000000
        storageData = {
            "remainingStorage": f'{gb}',
            "updatedAt": updatedAt,
        }
        serializer = BusinessFileSerializer(data=request_data)
        storageserializer = BusinessSerializer(businessStorage, data=storageData, partial=True)

        if serializer.is_valid(raise_exception=True) and storageserializer.is_valid(raise_exception=True):
            serializer.save()
            storageserializer.save()
            return created(message=f"{file_name} uploaded successfully")
        else:
            return bad_request(data=serializer.errors, message='Failed to upload file')

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'ownerId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the owner for whom to retrieve files.',
                required=True
            ),
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder from which to retrieve files.',
                required=True
            ),
        ],
        operation_id='get_business_files',
        operation_description='Get files in a specific folder for a given owner.'
    )
    def get(self, request):
        ownerId = request.GET.get('ownerId')
        folderId = request.GET.get('folderId')
        data = service.getBusinessFilesInFolder(ownerId, folderId)
        return ok(data=data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'fileId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the file to delete.',
                required=True
            ),
        ],
        operation_id='delete_business_file',
        operation_description='Delete a file by its ID.'
    )
    def delete(self, request):
        fileId = request.GET.get('fileId')
        file = DocumentBusinessFile.objects.filter(fileId=fileId).first()

        if file:
            file.isDeleted = True
            file.save()
            return ok(message='Successfully deleted')
        else:
            return ok(message='File Not Exist')


class CreateBusinessFolder(APIView):
    @swagger_auto_schema(
        operation_id='create_business_folder',
        operation_description='Create a new folder for a business.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'folderType': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Type of the folder (e.g., Business, Sub-Business, etc.).'),
                'folderPath': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Path of the folder within the business Directory.'),
                'businessId': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='ID of the business to which the folder belongs.'),
            },
            required=['folderType', 'folderPath', 'businessId']
        )
    )
    def post(self, request):
        try:
            folder_type = request.data.get('folderType')
            folder_path = request.data.get('folderPath')
            business_id = request.data.get('businessId')

            if not folder_path:
                return bad_request(message="Folder path is required")

            request_data = request.data
            current_datetime = datetime.datetime.now()
            request_data.update({
                'createdAt': current_datetime,
                'updatedAt': current_datetime,
                'size': 0,
                'ownerId': business_id
            })

            # Commented out Azure Blob Storage code
            # container_client = containerClient()
            # blob_name = f"{business_id}/{folder_path}/"
            # container_client.upload_blob(name=blob_name, data=b"")

            # Print statement for debugging
            print(f"Creating folder with the following details:\n"
                  f"Folder Type: {folder_type}\n"
                  f"Folder Path: {folder_path}\n"
                  f"Business ID: {business_id}")

            serializer = BusinessFolderSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return created(message=f"{serializer.data['folderName']} folder created successfully")

        except ResourceExistsError:
            return conflict(message=f"Business folder '{folder_path}' already exists.")
        except Exception as e:
            print(traceback.format_exc())
            return internal_server_error(message="Failed to create folder")


class CreateSubBusinessFolder(APIView):
    @swagger_auto_schema(
        operation_id='create_folder',
        operation_description='Create a new folder for a sub-business.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'folderType': openapi.Schema(type=openapi.TYPE_STRING),
                'folderPath': openapi.Schema(type=openapi.TYPE_STRING),
                'businessId': openapi.Schema(type=openapi.TYPE_STRING),
                'subBusinessId': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['folderType', 'folderPath', 'subBusinessId']
        )
    )
    def post(self, request):
        try:
            folder_type = request.data.get('folderType')
            folder_path = request.data.get('folderPath')
            business_id = request.data.get('businessId')
            sub_business_id = request.data.get('subBusinessId')

            if not folder_path:
                return bad_request(message="Folder path is required")

            request_data = request.data
            request_data.pop('businessId', None)
            current_datetime = datetime.datetime.now()
            request_data.update({
                'createdAt': current_datetime,
                'updatedAt': current_datetime,
                'size': 0,
                'ownerId': str(sub_business_id)
            })

            container_client = containerClient()
            blob_name = f"{business_id}/{sub_business_id}/{folder_path}"
            container_client.upload_blob(name=blob_name, data=b"")

            serializer = BusinessFolderSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return created(message=f"{serializer.data['folderName']} folder created successfully")

        except ResourceExistsError:
            return conflict(message=f"Business folder '{media}' already exists.")
        except Exception as e:
            print(traceback.format_exc())
            return internal_server_error(message="Failed to create folder")

    @swagger_auto_schema(
        operation_id='get_business_folder',
        operation_description='Retrieve business folder data.',
        manual_parameters=[
            openapi.Parameter(
                'parentId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the parent folder to retrieve data for.', required=True
            ),
        ]
    )
    def get(self, request):
        try:
            parent_id = request.GET.get('parentId')

            if not parent_id:
                return bad_request(message="Parent ID is required")

            data = service.getBusinessFolder(parent_id)
            return ok(data=data)

        except Exception as e:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to retrieve folder data')

    @swagger_auto_schema(
        operation_id='update_folder_name',
        operation_description='Update the name of a folder.',
        manual_parameters=[
            openapi.Parameter(
                'folderName', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='The new name for the folder.',
                required=True
            ),
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='The ID of the folder to update.',
                required=True
            ),
        ]
    )
    def patch(self, request):
        try:
            folder_name = request.GET.get('folderName')
            folder_id = request.GET.get('folderId')

            if not folder_name or not folder_id:
                return bad_request(message="Folder name and ID are required")

            DocumentBusinessFolder.objects.filter(folderId=folder_id).update(folderName=folder_name)
            return ok(message='Folder name updated successfully')

        except Exception as e:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to update folder name')

    @swagger_auto_schema(
        operation_id='delete_folder',
        operation_description='Delete a folder and its contents.',
        manual_parameters=[
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='The ID of the folder to delete.',
                required=True
            ),
        ]
    )
    def delete(self, request):
        try:
            folder_id = request.GET.get('folderId')

            if not folder_id:
                return bad_request(message="Folder ID is required")

            DocumentBusinessFolder.objects.filter(folderId=folder_id).update(isDeleted=True)
            DocumentBusinessFolder.objects.filter(folderParentId=folder_id).update(isDeleted=True)
            DocumentBusinessFile.objects.filter(folderId=folder_id).update(isDeleted=True)

            return ok(message='Folder deleted successfully')

        except Exception as e:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete folder')


class FilesFolders(APIView):
    @swagger_auto_schema(
        operation_id='get_files_in_folder',
        operation_description='Retrieve files in a folder by its ID.',
        manual_parameters=[
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to retrieve files from.', required=True
            ),
        ]
    )
    def get(self, request):
        try:
            folder_id = request.GET.get('folderId')

            if not folder_id:
                return bad_request(message="Folder ID is required")

            data = service.getFilesFolder(folder_id)
            return ok(data=data)

        except Exception as e:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to retrieve files in folder')


class UploadSubBusinessFiles(APIView):
    @swagger_auto_schema(
        operation_id='upload_file',
        operation_description='Upload a file to the server.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'requestType': openapi.Schema(type=openapi.TYPE_STRING),
                'filePath': openapi.Schema(type=openapi.TYPE_STRING),
                'ownerId': openapi.Schema(type=openapi.TYPE_STRING),
                'businessId': openapi.Schema(type=openapi.TYPE_STRING),
                'folderId': openapi.Schema(type=openapi.TYPE_STRING),
                'myFile': openapi.Schema(type=openapi.TYPE_FILE),
            },
            required=['requestType', 'filePath', 'ownerId', 'businessId', 'folderId', 'myFile'],
        )
    )
    def post(self, request):
        try:
            request_data = request.data
            requestType = request.data.get('requestType', None)
            filePath = request.data.get('filePath', None)
            ownerId = request.data.get('ownerId', None)
            businessId = request.data.get('businessId', None)
            folderId = request.data.get('folderId', None)
            file = request.FILES['myFile']
            file_name = request.FILES['myFile'].name
            updatedAt = datetime.datetime.now()
            businessStorage = Business.objects.get(businessId=businessId)
            serlizeData = BusinessSerializer(businessStorage)
            remainingStorage = serlizeData.data['remainingStorage']
            match = re.search(r'\d+(\.\d+)?', remainingStorage)

            # Get the matched number as a float
            number = float(match.group())
            kb = number * 1000000
            try:
                data = upload_file_to_azure_storagesub(file, businessId, ownerId, filePath, requestType)
                # Do something with the file URL, like save it to a database or display it in a template
                # data={'url': 'https://expertpreprodstorage.blob.core.windows.net/customer/129/myImagesss/personal/shield%20%281%29%20%281%29.png', 'size': 0.019143, 'type': 'image/png'}
                request_data['size'] = data['size']
                request_data['type'] = data['type']
                request_data['fileUrl'] = data['url']
                request_data['fileName'] = file_name
                request_data.pop('folderId')
                request_data.pop('businessId')
                request_data.pop('myFile')
                folder_obj = DocumentBusinessFolder.objects.get(folderId=folderId)
                # folderserializer = FolderSerlizer(folder_obj)
                request_data['folderId'] = folder_obj.folderId
                kb = kb - data['size']
                gb = kb / 1000000
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                storageserializer = BusinessSerializer(businessStorage, data=storageData, partial=True)
                serializer = BusinessFileSerializer(data=request_data)
                if serializer.is_valid(raise_exception=True) and storageserializer.is_valid(raise_exception=True):
                    serializer.save()
                    storageserializer.save()
                    return created(message=f"{file_name} uploaded successfully")
                else:
                    return bad_request(data=serializer.errors, message='Failed to upload file')
            except ResourceExistsError:
                # Handle the case when the container already exists
                return conflict(message=f"{file_name} already exists.")
            # List all blobs in the container
            # print(type(folder))
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message="Failed to create ")

    @swagger_auto_schema(
        operation_id='get_files_in_folder',
        operation_description='Get files in a specific folder.',
        manual_parameters=[
            openapi.Parameter(
                'ownerId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the owner of the folder.',
                required=True
            ),
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to retrieve files from.',
                required=True
            ),
        ]
    )
    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            folderId = request.GET.get('folderId', None)
            if folderId is not None:
                data = service.getBusinessFilesInFolder(ownerId, folderId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get files')

    @swagger_auto_schema(
        operation_id='delete_file',
        operation_description='Delete a file by its ID.',
        manual_parameters=[
            openapi.Parameter(
                'fileId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the file to be deleted.',
                required=True
            ),
        ]
    )
    def delete(self, request):
        try:
            fileId = request.GET.get('fileId', None)
            file = DocumentBusinessFile.objects.get(fileId=fileId)
            if file is None:
                return ok(message='File Not Exist')
            else:
                file.isDeleted = True
                file.save()
                return ok(message='Successfully deleted')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete file')
