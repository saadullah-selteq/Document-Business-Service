from django.db import models


class documentFolder(models.Model):
    folderId = models.AutoField(primary_key=True, blank=False)
    folderName = models.CharField(max_length=100, blank=True)
    folderPath = models.CharField(max_length=100, blank=True)
    folderParentId = models.CharField(max_length=100, blank=True)
    ownerId = models.CharField(max_length=100, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField(blank=True, default=0)
    folderType = models.CharField(max_length=100, blank=True)
    isPublic = models.BooleanField(blank=False, default=False)
    isLocked = models.BooleanField(blank=False, default=False)
    isDeleted = models.BooleanField(blank=False, default=False)
    permanantDelete = models.BooleanField(blank=False, default=False)
    permanantDeletedOn = models.DateTimeField(null=True, blank=True)


class documentFile(models.Model):
    fileId = models.AutoField(primary_key=True, blank=False)
    fileName = models.CharField(max_length=100, blank=True)
    filePath = models.CharField(max_length=100, blank=True)
    folderId = models.ForeignKey(documentFolder, on_delete=models.CASCADE, db_column="folderId")
    ownerId = models.CharField(max_length=100, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now_add=True)
    size = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)
    isPublic = models.BooleanField(blank=False, default=False)
    isReadOnly = models.BooleanField(blank=False, default=False)
    fileUrl = models.CharField(max_length=500, blank=True)
    isDeleted = models.BooleanField(blank=False, default=False)
    permanantDelete = models.BooleanField(blank=False, default=False)
    permanantDeletedOn = models.DateTimeField(null=True, blank=True)


class customer(models.Model):
    ownerId = models.IntegerField(primary_key=True, blank=False)
    isAdmin = models.BooleanField(blank=False, default=False)
    totalStorage = models.CharField(max_length=100, blank=True)
    remainingStorage = models.CharField(max_length=100, blank=True)
    package = models.CharField(max_length=100, blank=True)
    createdAt = models.DateTimeField(null=True, blank=True)
    updatedAt = models.DateTimeField(null=True, blank=True)
