import datetime
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from utils.util import get_package, get_package_date, containerClient
from msrest.exceptions import ValidationError
from utils.responses import  internal_server_error, bad_request, created, ok
from utils.util import containerClient
from documentBusinessService.serializer.BusinessFolderSerializer import BusinessFolderSerializer
from documentBusinessService.serializer.SubBusinessSerializer import SubBusinessSerializer
import traceback
from rest_framework.views import APIView
from documentBusinessService import service
from documentBusinessService.models import *
from utils.responses import internal_server_error, ok
import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from documentBusinessService.serializer.BusinessSerializer import BusinessSerializer


logger = logging.getLogger(__name__)


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

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
            status.HTTP_201_CREATED: openapi.Response(description='Business storage created successfully.'),
            status.HTTP_400_BAD_REQUEST: openapi.Response(description='Bad request.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(description='Internal server error.'),
        }
    )
    def create(self, request, *args, **kwargs):
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

        request_data = request.data.copy()
        request_data.update({
            'createdAt': today,
            'updatedAt': today,
            'isAdmin': True,
            'totalStorage': totalStorage,
            'remainingStorage': totalStorage,
            'expirationDate': expirationDate
        })

        dataFolder = {
            "folderName": businessId,
            "folderPath": f'{businessId}/',
            "ownerId": businessId,
            "folderType": "Business"
        }

        try:
            # container_client = containerClient()
            # container_client.upload_blob(name=f"{businessId}/", data=b"")

            print("Business creation logic reached")

            business_serializer = self.get_serializer(data=request_data)
            folder_serializer = BusinessFolderSerializer(data=dataFolder)

            if business_serializer.is_valid() and folder_serializer.is_valid():
                business_serializer.save()
                folder_serializer.save()
                return created(
                    message=f"{business_serializer.data['businessId']} Business storage created successfully")
            else:
                error_detail = business_serializer.errors or folder_serializer.errors
                return bad_request(data=error_detail, message="Invalid data")

        except Exception as e:
            logger.error("Failed to create business", exc_info=True)
            return internal_server_error(message="Failed to create business")

    @swagger_auto_schema(
        operation_id='retrieve_business',
        operation_description='Retrieve business data.',
        manual_parameters=[
            openapi.Parameter('businessId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='The ID of the business to retrieve.', required=True),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(description='Business data retrieved successfully.'),
            status.HTTP_400_BAD_REQUEST: openapi.Response(description='Bad request.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(description='Internal server error.'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        businessId = request.query_params.get('businessId')
        logger.debug(f"Business ID received: {businessId}")

        if not businessId:
            return bad_request(message="businessId is required")

        try:
            data = service.getBusiness(businessId)
            if not data:
                return bad_request(message="Business not found")

            return ok(data=data)

        except Exception as err:
            logger.error("Failed to get business", exc_info=True)
            return internal_server_error(message='Failed to get business')
"""""
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
            status.HTTP_200_OK: openapi.Response(description='Business storage updated successfully.'),
            status.HTTP_400_BAD_REQUEST: openapi.Response(description='Bad request.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(description='Internal server error.'),
        }
    )
    
    @action(detail=False, methods=['patch'], url_path='update-storage')
    def update_storage(self, request):
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
            updated_data = {
                'updatedAt': today,
                'totalStorage': totalStorage,
                'remainingStorage': totalStorage - int(business.totalStorage) + int(business.remainingStorage),
                'expirationDate': expirationDate
            }

            business_serializer = self.get_serializer(business, data=updated_data, partial=True)

            if business_serializer.is_valid():
                business_serializer.save()
                return ok(message=f"{business_serializer.data['businessId']} Business storage updated successfully")
            else:
                return bad_request(data=business_serializer.errors, message="Invalid data")

        except Business.DoesNotExist:
            return bad_request(message='Business does not exist')

        except Exception as e:
            logger.error("Failed to update storage", exc_info=True)
            return internal_server_error(message='Failed to update storage')

    @swagger_auto_schema(
        operation_id='delete_business_storage',
        operation_description='Delete business storage.',
        manual_parameters=[
            openapi.Parameter('folderId', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='The ID of the folder to delete.', required=True),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(description='Folder and associated files deleted successfully.'),
            status.HTTP_400_BAD_REQUEST: openapi.Response(description='Bad request.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(description='Internal server error.'),
        }
    )
    @action(detail=False, methods=['delete'], url_path='delete-storage')
    def delete_storage(self, request):
        folderId = request.query_params.get('folderId')
        if not folderId:
            return bad_request(message="folderId is required")

        try:
            DocumentBusinessFolder.objects.filter(folderId=folderId).update(isDeleted=True)
            DocumentBusinessFile.objects.filter(folderId=folderId).update(isDeleted=True)
            return ok(message='Successfully deleted')

        except Exception as err:
            logger.error("Failed to delete storage", exc_info=True)
            return internal_server_error(message='Failed to delete storage')

"""
class CreateSubBusiness(APIView):

    @swagger_auto_schema(
        operation_id='create_sub_business',
        operation_description='Create a sub-business.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'businessId': openapi.Schema(type=openapi.TYPE_STRING),
                'folderId': openapi.Schema(type=openapi.TYPE_STRING),
                'subBusinessId': openapi.Schema(type=openapi.TYPE_STRING),
                # Add other properties expected in the request body
            },
            required=['businessId', 'folderId', 'subBusinessId'],
        ))
    def post(self, request):
        try:
            businessId = request.data.get('businessId', None)
            folderId = request.data.get('folderId', None)
            subBusinessId = request.data.get('subBusinessId', None)
            getBusiness = Business.objects.get(businessId=businessId)
            today = datetime.datetime.now()
            if Business.objects.filter(businessId=businessId).exists():
                serlizer = BusinessSerializer(getBusiness)
                json_data = serlizer.data
            else:
                return bad_request(message='Business does not exist')

            dataFolder = {
                "folderName": subBusinessId,
                "folderPath": f'{subBusinessId}/',
                "folderParentId": folderId,
                "ownerId": subBusinessId,
                "createdAt": today,
                "updatedAt": today,
                "folderType": "SubBusiness"
            }
            if subBusinessId is not None:
                request_data = request.data
                request_data['createdAt'] = today
                request_data['updatedAt'] = today
                request_data['accessOf'] = f'{businessId}/'
                request_data['businessName'] = json_data['businessName']
                request_data['businessId'] = businessId
                try:
                    container_client = containerClient()
                    container_client.upload_blob(name=(str(businessId) + "/" + str(subBusinessId) + "/"), data=b"")
                    serializer = SubBusinessSerializer(data=request_data)
                    serializerFolder = BusinessFolderSerializer(data=dataFolder)
                    if serializer.is_valid(raise_exception=True) and serializerFolder.is_valid(raise_exception=True):
                        serializer.save()
                        serializerFolder.save()
                        return created(message=f"{serializer.data['subBusinessId']} subBusiness Created Successfully")
                    else:
                        error_detail = list(serializer.errors.values())[0][0]
                        return bad_request(data=serializer.errors, message=str(error_detail))
                except ValidationError as e:
                    error_detail = list(e.detail.values())[0][0]
                    return internal_server_error(message=str(error_detail))
            else:
                return bad_request(message="subBusinessId Id is missing")
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message="Failed to create")

    @swagger_auto_schema(
        operation_id='get_sub_business',
        operation_description='Retrieve sub-businesses for a given business.',
        manual_parameters=[
            openapi.Parameter(
                name='businessId',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='ID of the business to retrieve sub-businesses for.',
                required=True,
            ),
        ])
    def get(self, request):
        try:
            businessId = request.GET.get('businessId', None)
            if businessId is not None:
                data = service.getSubBusiness(businessId)
            return ok(data=data)
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get business')

    # def patch(self, request):
    #     try:
    #         businessId=request.data.get('businessId',None)
    #         package= request.data.get('package',None)
    #         package_details=get_package(package)
    #         today = datetime.datetime.now()
    #         if package_details != "Not found":
    #             totalStorage=package_details['storageLimit']
    #             Date=package_details['duration']
    #             expirationDate= get_package_date(Date)
    #         else:
    #             return bad_request( message='Package does not exist')
    #         getBusiness= Business.objects.get(businessId=businessId)
    #         if Business.objects.filter(businessId=businessId).exists():
    #             serlizer = BusinessSerlizer(getBusiness)
    #             json_data= serlizer.data
    #         print(json_data['remainingStorage'])
    #         print(totalStorage)
    #         print(json_data)
    #         usedStorage= int(json_data['totalStorage'])-int(json_data['remainingStorage'])
    #         remainingStorage=int(totalStorage)-usedStorage
    #         request_data= request.data
    #         request_data['updatedAt']=today
    #         request_data['totalStorage']=totalStorage
    #         request_data['remainingStorage']=remainingStorage
    #         request_data['expirationDate']=expirationDate
    #         serializer= BusinessSerlizer(getBusiness, data=request_data, partial=True)
    #         if serializer.is_valid(raise_exception=True):
    #             serializer.save()
    #             return ok(message=f"{serializer.data['businessId']} Business Updated Successfully")
    #         else:
    #             error_detail = list(serializer.errors.values())[0][0]
    #             return bad_request(data=serializer.errors, message=str(error_detail))
    #     except Exception as err:
    #         print(traceback.format_exc())
    #         return internal_server_error(message='Failed to update folder')
    @swagger_auto_schema(
        operation_id='delete_sub_business',
        operation_description='Delete a sub-business by its ID.',
        manual_parameters=[
            openapi.Parameter(
                name='subBusinessId',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='ID of the sub-business to delete.',
                required=True,
            ),
        ])
    def delete(self, request):
        try:
            subBusinessId = request.GET.get('subBusinessId', None)
            SubBusiness.objects.filter(subBusinessId=subBusinessId).update(isDeleted=True)
            return ok(message='Successfully deleted')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete folder')



class getSubBusinessDetails(APIView):
    @swagger_auto_schema(
        operation_id='get_sub_business_details',
        operation_description='Retrieve details of a sub-business by its ID.',
        manual_parameters=[
            openapi.Parameter(
                name='subBusinessId',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='ID of the sub-business to retrieve details for.',
                required=True,
            ),
        ])
    def get(self, request):
        try:
            subBusinessId = request.GET.get('subBusinessId', None)
            data = service.getSubBusinessDetails(subBusinessId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get file')

