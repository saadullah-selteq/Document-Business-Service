import traceback
from rest_framework.views import APIView
from documentBusinessService import service
from documentBusinessService.serializer import *
from documentBusinessService.models import *
from utils.responses import internal_server_error, ok
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class singlefile(APIView):
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
        try:
            fileId = request.GET.get('fileId', None)
            data = service.getSignleFile(fileId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get file')


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
        try:
            request_data = request.data
            requestType = request.data.get('requestType', None)
            filePath = request.data.get('filePath', None)
            ownerId = request.data.get('ownerId', None)
            folderId = request.data.get('folderId', None)
            file = request.FILES['myFile']
            file_name = request.FILES['myFile'].name
            updatedAt = datetime.datetime.now()
            businessStorage = Business.objects.get(businessId=ownerId)
            serlizeData = BusinessSerializer(businessStorage)
            remainingStorage = serlizeData.data['remainingStorage']
            match = re.search(r'\d+(\.\d+)?', remainingStorage)

            # Get the matched number as a float
            number = float(match.group())
            kb = number * 1000000
            try:
                data = upload_file_to_azure_storage(file, ownerId, filePath, requestType)
                # Do something with the file URL, like save it to a database or display it in a template
                # data={'url': 'https://expertpreprodstorage.blob.core.windows.net/customer/129/myImagesss/personal/shield%20%281%29%20%281%29.png', 'size': 0.019143, 'type': 'image/png'}
                request_data['size'] = data['size']
                request_data['type'] = data['type']
                request_data['fileUrl'] = data['url']
                request_data['fileName'] = file_name
                request_data.pop('folderId')
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
                serializer = BusinessFileSerializer(data=request_data)
                storageserializer = BusinessSerializer(businessStorage, data=storageData, partial=True)
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
        try:
            fileId = request.GET.get('fileId', None)
            delete_datetime = datetime.datetime.now()
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

