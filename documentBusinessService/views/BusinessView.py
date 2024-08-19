import traceback
import logging
import datetime

from msrest.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from documentBusinessService import service
from documentBusinessService.models import Business, DocumentBusinessFolder, DocumentBusinessFile
from documentBusinessService.serializer.BusinessFolderSerializer import BusinessFolderSerializer
from documentBusinessService.serializer.BusinessSerializer import BusinessSerializer
from utils.responses import internal_server_error, bad_request, created, ok
from utils.util import get_package, get_package_date, containerClient

# Set up logging
logger = logging.getLogger(__name__)


class CreateBusiness(APIView):

    @swagger_auto_schema(
        operation_id='create_business',
        operation_description='Create a new business and associated storage.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'businessId': openapi.Schema(type=openapi.TYPE_STRING, description='The ID of the business.'),
                'package': openapi.Schema(type=openapi.TYPE_STRING,
                                          description='The package name associated with the business.'),
            },
            required=['businessId', 'package'],
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description='Business storage created successfully.',
                examples={'application/json': {'message': 'Business storage created Successfully'}}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request.',
                examples={'application/json': {'message': 'businessId and package are required'}}
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description='Internal server error.',
                examples={'application/json': {'message': 'Failed to process the request'}}
            ),
        }
    )
    def post(self, request):
        try:
            businessId = request.data.get('businessId')
            package = request.data.get('package')

            if not businessId or not package:
                return bad_request(message="businessId and package are required")

            package_details = get_package(package)
            if package_details == "Not found":
                return bad_request(message='Package does not exist')

            today = datetime.datetime.now()
            totalStorage = package_details['storageLimit']
            expirationDate = get_package_date(package_details['duration'])

            dataFolder = {
                "folderName": businessId,
                "folderPath": f'{businessId}/',
                "folderParentId": "",
                "ownerId": businessId,
                "createdAt": today,
                "updatedAt": today,
                "folderType": "Business"
            }

            request_data = request.data.copy()
            request_data.update({
                'createdAt': today,
                'updatedAt': today,
                'isAdmin': True,
                'totalStorage': totalStorage,
                'remainingStorage': totalStorage,
                'expirationDate': expirationDate
            })

            try:
                container_client = containerClient()
                container_client.upload_blob(name=f"{businessId}/", data=b"")

                serializer = BusinessSerializer(data=request_data)
                serializerFolder = BusinessFolderSerializer(data=dataFolder)

                if serializer.is_valid() and serializerFolder.is_valid():
                    serializer.save()
                    serializerFolder.save()
                    return created(message=f"{serializer.data['businessId']} Business storage created successfully")
                else:
                    error_detail = list(serializer.errors.values())[0][0]
                    return bad_request(data=serializer.errors, message=str(error_detail))

            except ValidationError as e:
                error_detail = list(e.detail.values())[0][0]
                return internal_server_error(message=str(error_detail))
            except Exception as e:
                logger.error("Failed to process the request", exc_info=True)
                return internal_server_error(message="Failed to process the request")

        except Exception as err:
            logger.error("Failed to create business", exc_info=True)
            return internal_server_error(message="Failed to create business")

    @swagger_auto_schema(
        operation_id='get_business',
        operation_description='Retrieve business data.',
        manual_parameters=[
            openapi.Parameter(
                'businessId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the business to retrieve.',
                required=True
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Business data retrieved successfully.',
                examples={'application/json': {'data': {}}}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request.',
                examples={'application/json': {'message': 'businessId is required'}}
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description='Internal server error.',
                examples={'application/json': {'message': 'Failed to get Business'}}
            ),
        }
    )
    def get(self, request):
        try:
            businessId = request.GET.get('businessId')
            if not businessId:
                return bad_request(message="businessId is required")

            data = service.getBusiness(businessId)
            if not data:
                return bad_request(message="Business not found")

            return ok(data=data)

        except Exception as err:
            logger.error("Failed to get business", exc_info=True)
            return internal_server_error(message='Failed to get business')

    @swagger_auto_schema(
        operation_id='update_business_storage',
        operation_description='Update business storage details.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'businessId': openapi.Schema(type=openapi.TYPE_STRING, description='The ID of the business.'),
                'package': openapi.Schema(type=openapi.TYPE_STRING, description='The new package name.'),
            },
            required=['businessId', 'package'],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Business storage updated successfully.',
                examples={'application/json': {'message': 'Business storage updated successfully'}}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request.',
                examples={'application/json': {'message': 'businessId and package are required'}}
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description='Internal server error.',
                examples={'application/json': {'message': 'Failed to update storage'}}
            ),
        }
    )
    def patch(self, request):
        try:
            businessId = request.data.get('businessId')
            package = request.data.get('package')

            if not businessId or not package:
                return bad_request(message="businessId and package are required")

            package_details = get_package(package)
            if package_details == "Not found":
                return bad_request(message='Package does not exist')

            today = datetime.datetime.now()
            totalStorage = package_details['storageLimit']
            expirationDate = get_package_date(package_details['duration'])

            try:
                business = Business.objects.get(businessId=businessId)
                serializer = BusinessSerializer(business, data={
                    'updatedAt': today,
                    'totalStorage': totalStorage,
                    'remainingStorage': totalStorage - int(business.totalStorage) + int(business.remainingStorage),
                    'expirationDate': expirationDate
                }, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    return ok(message=f"{serializer.data['businessId']} Business storage updated successfully")
                else:
                    error_detail = list(serializer.errors.values())[0][0]
                    return bad_request(data=serializer.errors, message=str(error_detail))

            except Business.DoesNotExist:
                return bad_request(message='Business does not exist')

            except Exception as e:
                logger.error("Failed to update storage", exc_info=True)
                return internal_server_error(message='Failed to update storage')

        except Exception as err:
            logger.error("Failed to update storage", exc_info=True)
            return internal_server_error(message='Failed to update storage')

    @swagger_auto_schema(
        operation_id='delete_business_storage',
        operation_description='Delete business storage.',
        manual_parameters=[
            openapi.Parameter(
                'folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='The ID of the folder to delete.',
                required=True
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Folder and associated files deleted successfully.',
                examples={'application/json': {'message': 'Successfully deleted'}}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request.',
                examples={'application/json': {'message': 'folderId is required'}}
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description='Internal server error.',
                examples={'application/json': {'message': 'Failed to delete storage'}}
            ),
        }
    )
    def delete(self, request):
        try:
            folderId = request.GET.get('folderId')
            if not folderId:
                return bad_request(message="folderId is required")

            DocumentBusinessFolder.objects.filter(folderId=folderId).update(isDeleted=True)
            DocumentBusinessFile.objects.filter(folderId=folderId).update(isDeleted=True)
            return ok(message='Successfully deleted')

        except Exception as err:
            logger.error("Failed to delete storage", exc_info=True)
            return internal_server_error(message='Failed to delete storage')
