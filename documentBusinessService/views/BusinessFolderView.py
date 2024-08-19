import traceback
from msrest.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from documentBusinessService import service
from documentBusinessService.serializer import *
from documentBusinessService.models import *
from utils.responses import conflict, internal_server_error, bad_request, created, ok
from utils.util import get_package, get_package_date, validate_page_number, containerClient
import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from azure.core.exceptions import ResourceExistsError
from documentBusinessService.serializer.BusinessFolderSerializer import BusinessFolderSerializer


class CreateBusinessFolder(APIView):
    @swagger_auto_schema(
        operation_id='create_business_folder',
        operation_description='Create a new folder for a business.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'folderType': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Type of the folder (e.g., Business, Sub-Business, etc.).',
                ),
                'folderPath': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Path of the folder within the business Directory.',
                ),
                'businessId': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='ID of the business to which the folder belongs.',
                ),
            },
            required=['folderType', 'folderPath', 'businessId'],  # Adjust as per your requirements
        ))
    def post(self, request):
        try:
            folderType = request.data.get('folderType', None)
            folderPath = request.data.get('folderPath', None)
            businessId = request.data.get('businessId', None)
            if folderPath is not None:
                request_data = request.data
                current_datetime = datetime.datetime.now()
                request_data['createdAt'] = current_datetime
                request_data['updatedAt'] = current_datetime
                request_data['size'] = 0
                request_data['ownerId'] = businessId
                try:
                    container_client = containerClient()
                    container_client.upload_blob(name=(str(businessId) + "/" + str(folderPath) + "/"), data=b"")

                    try:
                        serializer = BusinessFolderSerializer(data=request_data)
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                            return created(message=f"{serializer.data['folderName']} Folder Created Successfully")
                        else:
                            return bad_request(data=serializer.errors, message='Failed to create Event')
                    except ResourceExistsError:
                        # Handle the case when the container already exists
                        return conflict(message=f"Business folder '{folderPath}' already exists.")

                except Exception as e:
                    print(traceback.format_exc())
                    return internal_server_error(message="Failed to create folder")
            else:
                return bad_request(message="Folder path does not exist")
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message="Failed to create folder")


class CreateSubBusinessFolder(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'folderType': openapi.Schema(type=openapi.TYPE_STRING),
                'folderPath': openapi.Schema(type=openapi.TYPE_STRING),
                'businessId': openapi.Schema(type=openapi.TYPE_STRING),
                'subBusinessId': openapi.Schema(type=openapi.TYPE_STRING),
                # Add other properties expected in the request body
            },
            required=['folderType', 'folderPath', 'subBusinessId'],
        ),
        operation_id='create_folder',
        operation_description='Create a new folder.'
    )
    def post(self, request):
        try:
            folderType = request.data.get('folderType', None)
            folderPath = request.data.get('folderPath', None)
            businessId = request.data.get('businessId', None)
            subBusinessId = request.data.get('subBusinessId', None)
            if folderPath is not None:
                request_data = request.data
                request_data.pop('businessId')
                current_datetime = datetime.datetime.now()
                request_data['createdAt'] = current_datetime
                request_data['updatedAt'] = current_datetime
                request_data['size'] = 0
                request_data['ownerId'] = str(subBusinessId)
                try:
                    container_client = containerClient()
                    container_client.upload_blob(
                        name=(str(businessId) + "/" + str(subBusinessId) + "/" + str(folderPath)), data=b"")
                    try:
                        serializer = BusinessFolderSerializer(data=request_data)
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                            return created(message=f"{serializer.data['folderName']} Folder Created Successfully")
                        else:
                            return bad_request(data=serializer.errors, message='Failed to create Event')
                    except ResourceExistsError:
                        # Handle the case when the container already exists
                        return conflict(message=f"Business folder '{folderPath}' already exists.")

                except Exception as e:
                    print(traceback.format_exc())
                    return internal_server_error(message="Failed to create folder")
            else:
                return bad_request(message="Folder path does not exist")
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message="Failed to create folder")

    @swagger_auto_schema(
        operation_id='get_business_folder',
        operation_description='Get business folder data.',
        manual_parameters=[
            openapi.Parameter(
                'parentId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the parent folder to retrieve data for.',
                required=True
            ),
        ]
    )
    def get(self, request):
        try:
            parentId = request.GET.get('parentId', None)
            if parentId is not None:
                data = service.getBusinessFolder(parentId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get folder')

    @swagger_auto_schema(
        operation_id='update_folder_name',
        operation_description='Update folder name.',
        manual_parameters=[
            openapi.Parameter(
                'folderName', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The new name for the folder.',
                required=True
            ),
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to update.',
                required=True
            ),
        ]
    )
    def patch(self, request):
        try:
            folderName = request.GET.get('folderName', None)
            folderId = request.GET.get('folderId', None)
            DocumentBusinessFolder.objects.filter(folderId=folderId).update(folderName=folderName)
            return ok(message='Successfully updated name')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to update folder')

    @swagger_auto_schema(
        operation_id='delete_folder',
        operation_description='Delete folder and its contents.',
        manual_parameters=[
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to delete.',
                required=True
            ),
        ]
    )
    def delete(self, request):
        try:
            folderId = request.GET.get('folderId', None)
            DocumentBusinessFolder.objects.filter(folderId=folderId).update(isDeleted=True)
            DocumentBusinessFolder.objects.filter(folderParentId=folderId).update(isDeleted=True)
            DocumentBusinessFile.objects.filter(folderId=folderId).update(isDeleted=True)
            return ok(message='Successfully deleted')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete folder')



class filesfolders(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to retrieve files from.',
                required=True
            ),
        ],
        operation_id='get_files_in_folder',
        operation_description='Retrieve files in a folder by its ID.'
    )
    def get(self, request):
        try:
            folderId = request.GET.get('folderId', None)
            if folderId is not None:
                data = service.getFilesFolder(folderId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get bookings')
