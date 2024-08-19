
from .models import *
from documentBusinessService.serializer import *
from .serializer.BusinessFileSerializer import BusinessFileSerializer
from .serializer.BusinessFolderSerializer import BusinessFolderSerializer
from .serializer.BusinessSerializer import BusinessSerializer
from .serializer.SubBusinessSerializer import SubBusinessSerializer


def getBusiness(businessId):
    data = Business.objects.filter(businessId=businessId)
    folder = DocumentBusinessFolder.objects.filter(ownerId=businessId, isDeleted=False)
    if data.exists():
        serlizer = BusinessSerializer(data, many=True)
        serlizerFolder = BusinessFolderSerializer(folder, many=True)
        json_data = serlizer.data
        json_data1 = serlizerFolder.data
        data = {'Business': json_data, 'business_folder': json_data1[0]}
    else:
        data = []
    return data


def getSubBusiness(businessId):
    data = SubBusiness.objects.filter(businessId=businessId, isDeleted=False)
    if data.exists():
        serlizer = SubBusinessSerializer(data, many=True)
        json_data = serlizer.data
    else:
        json_data = []
    return json_data


def getBusinessFolder(parentId):
    data = DocumentBusinessFolder.objects.filter(folderParentId=parentId, isDeleted=False)
    if data.exists():
        serlizer = BusinessFolderSerializer(data, many=True)
        json_data = serlizer.data
    else:
        json_data = []
    return json_data


def getBusinessFilesInFolder(ownerId, folderId):
    data = DocumentBusinessFile.objects.filter(ownerId=ownerId, folderId=folderId, isDeleted=False)
    if data.exists():
        serlizer = BusinessFileSerializer(data, many=True)
        json_data = serlizer.data
    else:
        json_data = []
    return json_data


def getSignleFile(fileId):
    try:
        data = DocumentBusinessFile.objects.filter(fileId=fileId, isDeleted=False)
        serlizer = BusinessFileSerializer(data, many=True)
        json_data = serlizer.data
    except DocumentBusinessFile.DoesNotExist:
        json_data = "not exist"
    return json_data


def getFilesFolder(folderId):
    json_data = []
    filedata = DocumentBusinessFile.objects.filter(folderId=folderId, isDeleted=False)
    if filedata.exists():
        serlizer = BusinessFileSerializer(filedata, many=True)
        json_data1 = serlizer.data
        json_data.append({"files": json_data1})
    folderdata = DocumentBusinessFolder.objects.filter(folderParentId=folderId, isDeleted=False)
    if folderdata.exists():
        serlizer2 = BusinessFolderSerializer(folderdata, many=True)
        json_data2 = serlizer2.data
        json_data.append({"folder": json_data2})
    return json_data


def getSubBusinessDetails(subBusinessId):
    data = SubBusiness.objects.filter(subBusinessId=subBusinessId, isDeleted=False)
    folder = DocumentBusinessFolder.objects.filter(ownerId=subBusinessId, isDeleted=False)
    if data.exists():
        serlizer = SubBusinessSerializer(data, many=True)
        serlizerFolder = BusinessFolderSerializer(folder, many=True)
        json_data = serlizer.data
        json_data1 = serlizerFolder.data
        print(json_data1)
        data = {'SubBusiness': json_data, 'subbusiness_folder': json_data1[0]}
    else:
        data = []
    return data


def getRecycleBin(ownerId):
    json_data1 = []
    json_data2 = []
    files = []
    filedata = DocumentBusinessFile.objects.filter(ownerId=ownerId, isDeleted=True, permanentDelete=False)
    if filedata.exists():
        serlizer = BusinessFileSerializer(filedata, many=True)
        json_data1 = serlizer.data
    folderdata = DocumentBusinessFolder.objects.filter(ownerId=ownerId, isDeleted=True, permanentDelete=False)
    if folderdata.exists():
        serlizer2 = BusinessFolderSerializer(folderdata, many=True)
        json_data2 = serlizer2.data

    folder_ids = [folder['folderId'] for folder in json_data2]
    filtered_folders = [folder for folder in json_data2 if int(folder['folderParentId']) not in folder_ids]
    if json_data2:
        for folder in filtered_folders:
            for file in json_data1:
                if file['folderId'] == folder['folderId']:
                    print("deleted")
                else:
                    files.append(file)
                    print(file)
    else:
        if json_data1:
            files = json_data1
    json_data = {"folder": filtered_folders, "files": files}
    return json_data
