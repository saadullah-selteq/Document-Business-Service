import json
import requests
from .models import *
from .serlizer import *


def getCustomerFolder(ownerId, parentId):
    data = documentFolder.objects.filter(ownerId=ownerId, folderParentId=parentId, isDeleted=False)
    if data.exists():
        serlizer = FolderSerlizer(data, many=True)
        json_data = serlizer.data
    else:
        json_data = []
    return json_data


def getCustomerFilesInFolder(ownerId, folderId):
    data = documentFile.objects.filter(ownerId=ownerId, folderId=folderId, isDeleted=False)

    if data.exists():
        serlizer = FileSerializer(data, many=True)
        json_data = serlizer.data
    else:
        json_data = []
    return json_data


def getSignleFile(fileId):
    try:
        data = documentFile.objects.filter(fileId=fileId, isDeleted=False)
        serlizer = FileSerializer(data, many=True)
        json_data = serlizer.data
    except documentFile.DoesNotExist:
        json_data = "not exist"
    return json_data


def getFilesFolder(folderId):
    json_data = []
    filedata = documentFile.objects.filter(folderId=folderId, isDeleted=False)
    if filedata.exists():
        serlizer = FileSerializer(filedata, many=True)
        json_data1 = serlizer.data
        json_data.append({"files": json_data1})
    folderdata = documentFolder.objects.filter(folderParentId=folderId, isDeleted=False)
    if folderdata.exists():
        serlizer2 = FolderSerlizer(folderdata, many=True)
        json_data2 = serlizer2.data
        json_data.append({"folder": json_data2})
    return json_data


from typing import List, Dict
from collections import OrderedDict


def remove_duplicate_folders(folders: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # Create a set to keep track of folder IDs that are parent folders
    parent_folder_ids = set()

    # Create a new list to store the non-duplicate folders
    new_folders = []

    # Iterate through the folders
    for folder in folders:
        # Check if the folderParentId is in the parent_folder_ids set
        if folder['folderParentId'] in parent_folder_ids:
            continue  # skip this folder if it has a duplicate parent

        # Add the folder ID to the parent_folder_ids set
        parent_folder_ids.add(str(folder['folderId']))

        # Append the folder to the new_folders list
        new_folders.append(folder)

    return new_folders


def getRecycleBin(ownerId):
    json_data1 = []
    json_data2 = []
    files = []
    filedata = documentFile.objects.filter(ownerId=ownerId, isDeleted=True, permanantDelete=False)
    if filedata.exists():
        serlizer = FileSerializer(filedata, many=True)
        json_data1 = serlizer.data

    folderdata = documentFolder.objects.filter(ownerId=ownerId, isDeleted=True, permanantDelete=False)
    if folderdata.exists():
        serlizer2 = FolderSerlizer(folderdata, many=True)
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


def getUserRootId(ownerId):
    try:
        data = documentFolder.objects.filter(ownerId=ownerId, folderName="root")
        serlizer = FolderSerlizer(data, many=True)
        json_data = serlizer.data
    except documentFile.DoesNotExist:
        json_data = "not exist"
    return json_data


def getUserStorage(ownerId):
    try:
        data = customer.objects.get(ownerId=ownerId)
        serlizer = UserStorageSerlizer(data)
        json_data = serlizer.data
    except documentFile.DoesNotExist:
        json_data = "not exist"
    return json_data
