import traceback
from msrest.exceptions import ValidationError
from rest_framework.views import APIView
from documentBusinessService import service
from documentBusinessService.models import *
from utils.responses import  internal_server_error, bad_request, created, ok
from utils.util import containerClient
import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from documentBusinessService.serializer.BusinessFolderSerializer import BusinessFolderSerializer
from documentBusinessService.serializer.BusinessSerializer import BusinessSerializer
from documentBusinessService.serializer.SubBusinessSerializer import SubBusinessSerializer
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
import traceback
from msrest.exceptions import ValidationError
from rest_framework.views import APIView
from documentBusinessService import service
from utils.responses import internal_server_error, bad_request, created, ok

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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


class emptyconatiner(APIView):
    def delete(self, request):
        try:
            folderPath = request.data.get('folderPath', None)
            conatiner = "customer"
            delete_virtual_directory(conatiner, folderPath)
            return ok(message='Successfully empty recycle bin')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete file')
