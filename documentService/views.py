
import traceback
# from scheduler_backend import secrets
from rest_framework.views import APIView
from documentService import service
from .serlizer import *
from .models import *
from core import  secrets
from utils.responses import conflict, internal_server_error, bad_request, created,  ok
from azure.storage.blob import ContentSettings
from azure.core.exceptions import ResourceExistsError
import datetime
from utils.util import *


def upload_file_to_azure_storage(file, ownerId, virtual_directory, container_name):

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


def delete_virtual_directory(container_name, directory_path):
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=secrets.AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)
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


class CreateFolder(APIView):
    def post(self, request):
        try:
            folderType = request.data.get('folderType', None)
            folderPath = request.data.get('folderPath', None)
            folderRequest = request.data.get('folderRequest', None)
            ownerId = request.data.get('ownerId', None)
            folder = ownerId
            createdAt = datetime.datetime.now()

            if folderPath is not None:
                request_data = request.data
                current_datetime = datetime.datetime.now()
                request_data['createdAt'] = current_datetime
                request_data['updatedAt'] = current_datetime
                request_data['size'] = 0
                try:
                    container_client = containerClient()
                    # Check if the container exists
                    container_exists = container_client.exists()

                    if container_exists:
                        print(f"Container  exists.")
                    else:
                        print(f"Container  does not exist.")
                    if folderRequest == "new user":
                        userStorage = {
                            "userId": ownerId,
                            "isAdmin": True,
                            "totalStorage": "1",
                            "remainingStorage": "1",
                            "package": "default",
                            "createdAt": createdAt,
                            "updatedAt": createdAt,
                        }
                        try:
                            f_name = f"customer/{folder}/"
                            folder_blob_name = f_name

                            # Create a blob with the nested directory structure
                            blob_client = container_client.get_blob_client(folder_blob_name)
                            blob_client.upload_blob(b'')

                            print(f"Nested directory '{f_name}' created in the container.")
                            serializer = FolderSerlizer(data=request_data)
                            userstorageserializer = UserStorageSerlizer(data=userStorage)
                            if serializer.is_valid(raise_exception=True) and userstorageserializer.is_valid(
                                    raise_exception=True):
                                serializer.save()
                                userstorageserializer.save()
                                return created(message=f"{serializer.data['folderName']} Folder Created Successfully")
                            else:
                                return bad_request(data=serializer.errors, message='Failed to create Event')
                        except ResourceExistsError:
                            # Handle the case when the container already exists
                            return conflict(message=f"User id'{folder}' already exists.")
                    else:
                        try:
                            container_client.upload_blob(name=(folder + "/" + folderPath), data=b"")
                            serializer = FolderSerlizer(data=request_data)
                            if serializer.is_valid(raise_exception=True):
                                serializer.save()
                                return created(message=f"{serializer.data['folderName']} Folder Created Successfully")
                            else:
                                return bad_request(data=serializer.errors, message='Failed to create Event')
                        except ResourceExistsError:
                            # Handle the case when the container already exists
                            return conflict(message=f"User folder '{folderPath}' already exists.")

                except Exception as e:
                    print(traceback.format_exc())
                    return internal_server_error(message="Failed to create folder")
            else:
                return bad_request(message="Folder parent or Name is missing")
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message="Failed to create folder")

    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            parentId = request.GET.get('parentId', None)
            if parentId is not None:
                data = service.getCustomerFolder(ownerId, parentId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get bookings')

    def patch(self, request):
        try:
            folderName = request.GET.get('folderName', None)
            folderId = request.GET.get('folderId', None)
            documentFolder.objects.filter(folderId=folderId).update(folderName=folderName)
            return ok(message='Successfully updated name')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to update folder')

    def delete(self, request):
        try:
            folderId = request.GET.get('folderId', None)
            documentFolder.objects.filter(folderId=folderId).update(isDeleted=True)
            documentFolder.objects.filter(folderParentId=folderId).update(isDeleted=True)
            documentFile.objects.filter(folderId=folderId).update(isDeleted=True)
            return ok(message='Successfully deleted')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete folder')


class uploadFile(APIView):
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
            userStorage = customer.objects.get(ownerId=ownerId)
            serlizeData = UserStorageSerlizer(userStorage)
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
                request_data.pop('requestType')
                request_data.pop('myFile')
                folder_obj = documentFolder.objects.get(folderId=folderId)
                # folderserializer = FolderSerlizer(folder_obj)
                request_data['folderId'] = folder_obj.folderId
                kb = kb - data['size']
                gb = kb / 1000000
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                serializer = FileSerializer(data=request_data)
                storageserializer = UserStorageSerlizer(userStorage, data=storageData, partial=True)

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

    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            folderId = request.GET.get('folderId', None)
            if folderId is not None:
                data = service.getCustomerFilesInFolder(ownerId, folderId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get bookings')

    def delete(self, request):
        try:
            fileId = request.GET.get('fileId', None)
            delete_datetime = datetime.datetime.now()
            file = documentFile.objects.get(fileId=fileId)
            if file is None:
                return ok(message='File Not Exist')
            else:
                file.isDeleted = True
                file.save()
                return ok(message='Successfully deleted')
        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to delete file')


class singlefile(APIView):
    def get(self, request):
        try:
            fileId = request.GET.get('fileId', None)
            documentFile.objects.filter(fileId=fileId).update(isDeleted=True)
            data = service.getSignleFile(fileId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get file')


class filesfolders(APIView):
    def get(self, request):
        try:
            folderId = request.GET.get('folderId', None)
            if folderId is not None:
                data = service.getFilesFolder(folderId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get bookings')


class emptyrecyclebin(APIView):
    def post(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            type = request.GET.get('type', None)
            if type == "all":
                documentFolder.objects.filter(ownerId=ownerId, permanantDelete=False).update(isDeleted=False)
                documentFile.objects.filter(ownerId=ownerId, permanantDelete=False).update(isDeleted=False)
                return ok(message="Successfull restore data")

            elif type == "folder":
                folderId = request.GET.get('folderId', None)
                documentFolder.objects.filter(folderId=folderId, permanantDelete=False).update(isDeleted=False)
                documentFolder.objects.filter(folderParentId=folderId, permanantDelete=False).update(isDeleted=False)
                documentFile.objects.filter(folderId=folderId, permanantDelete=False).update(isDeleted=False)
                return ok(message="Successfull folder restore")
            elif type == "file":
                fileId = request.GET.get('fileId', None)
                documentFile.objects.filter(fileId=fileId, permanantDelete=False).update(isDeleted=False)
                return ok(message="Successfull file restore")

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get bookings')

    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            if ownerId is not None:
                data = service.getRecycleBin(ownerId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get bookings')

    def delete(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            delete_datetime = datetime.datetime.now()
            type = request.GET.get('type', None)
            updatedAt = datetime.datetime.now()
            userStorage = customer.objects.get(ownerId=ownerId)
            serlizeData = UserStorageSerlizer(userStorage)
            remainingStorage = serlizeData.data['remainingStorage']
            match = re.search(r'\d+(\.\d+)?', remainingStorage)
            # Get the matched number as a float
            number = float(match.group())
            kb = number * 1000000
            if type == "all":
                files = documentFile.objects.filter(ownerId=ownerId, isDeleted=True, permanantDelete=False)
                fileSerilzer = FileSerializer(files, many=True)
                data = fileSerilzer.data
                total_size = sum(float(item['size']) for item in data)
                kb = kb + total_size
                gb = kb / 1000000
                print(gb)
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                storageserializer = UserStorageSerlizer(userStorage, data=storageData, partial=True)
                if storageserializer.is_valid(raise_exception=True):
                    storageserializer.save()
                    documentFolder.objects.filter(ownerId=ownerId, isDeleted=True, permanantDelete=False).update(
                        permanantDelete=True, permanantDeletedOn=delete_datetime)
                    documentFile.objects.filter(ownerId=ownerId, isDeleted=True, permanantDelete=False).update(
                        permanantDelete=True, permanantDeletedOn=delete_datetime)
                    return ok(message='Successfully empty recycle bin')

            elif type == "folder":
                folderId = request.GET.get('folderId', None)
                files = documentFile.objects.filter(folderId=folderId, isDeleted=True)
                fileSerilzer = FileSerializer(files, many=True)
                data = fileSerilzer.data
                total_size = sum(float(item['size']) for item in data)
                kb = kb + total_size
                gb = kb / 1000000
                print(gb)
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                storageserializer = UserStorageSerlizer(userStorage, data=storageData, partial=True)
                if storageserializer.is_valid(raise_exception=True):
                    storageserializer.save()
                    documentFolder.objects.filter(folderId=folderId, isDeleted=True, permanantDelete=False).update(
                        permanantDelete=True, permanantDeletedOn=delete_datetime)
                    documentFolder.objects.filter(folderParentId=folderId, isDeleted=True,
                                                  permanantDelete=False).update(permanantDelete=True,
                                                                                permanantDeletedOn=delete_datetime)
                    documentFile.objects.filter(folderId=folderId, isDeleted=True, permanantDelete=False).update(
                        permanantDelete=True, permanantDeletedOn=delete_datetime)
                    return ok(message='Successfully folder permanent delete')
            elif type == "file":
                fileId = request.GET.get('fileId', None)
                file = documentFile.objects.filter(fileId=fileId, isDeleted=True)
                fileSerilzer = FileSerializer(file, many=True)
                data = fileSerilzer.data
                print(data)
                kb = kb + float(data[0]['size'])
                gb = kb / 1000000
                print(gb)
                storageData = {
                    "remainingStorage": f'{gb}',
                    "updatedAt": updatedAt,
                }
                storageserializer = UserStorageSerlizer(userStorage, data=storageData, partial=True)
                if storageserializer.is_valid(raise_exception=True):
                    storageserializer.save()
                    documentFile.objects.filter(fileId=fileId, isDeleted=True, permanantDelete=False).update(
                        permanantDelete=True, permanantDeletedOn=delete_datetime)
                    return ok(message='Successfully file permanent delete')



        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to permanent delete')


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


class userroot(APIView):
    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            if ownerId is not None:
                data = service.getUserRootId(ownerId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get storage')


class userdetails(APIView):
    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            if ownerId is not None:
                data = service.getUserStorage(ownerId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get user')
