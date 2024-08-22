from django.db import models


class BaseModel(models.Model):
    isDeleted = models.BooleanField(blank=False, default=False)
    permanentDelete = models.BooleanField(blank=False, default=False)
    permanentDeletedOn = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DocumentBusinessFolder(BaseModel):
    folderId = models.AutoField(primary_key=True, blank=False)
    folderName = models.CharField(max_length=100, blank=True)
    folderPath = models.CharField(max_length=100, blank=True)
    blobFolderName = models.CharField(max_length=100, blank=True)
    blobFolderPath = models.CharField(max_length=100, blank=True)
    folderParentId = models.CharField(max_length=100, blank=True)
    ownerId = models.CharField(max_length=100, blank=True)
    size = models.IntegerField(blank=True, default=0)
    folderType = models.CharField(max_length=100, blank=True)
    isPublic = models.BooleanField(blank=False, default=False)
    isLocked = models.BooleanField(blank=False, default=False)


class DocumentBusinessFile(BaseModel):
    fileId = models.AutoField(primary_key=True, blank=False)
    fileName = models.CharField(max_length=100, blank=True)
    filePath = models.CharField(max_length=100, blank=True)
    blobFileName = models.CharField(max_length=100, blank=True)
    blobFilePath = models.CharField(max_length=100, blank=True)
    folderId = models.ForeignKey(DocumentBusinessFolder, on_delete=models.CASCADE, db_column="folderId")
    ownerId = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)
    isPublic = models.BooleanField(blank=False, default=False)
    isReadOnly = models.BooleanField(blank=False, default=False)
    fileUrl = models.CharField(max_length=500, blank=True)


class Business(models.Model):
    businessId = models.IntegerField(primary_key=True, blank=False)
    businessName = models.CharField(max_length=100, blank=True)
    isAdmin = models.BooleanField(blank=False, default=False)
    totalStorage = models.CharField(max_length=100, blank=True)
    remainingStorage = models.CharField(max_length=100, blank=True)
    expirationDate = models.DateTimeField(blank=False, null=False)
    package = models.CharField(max_length=100, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(blank=True, null=True)


class SubBusiness(models.Model):
    subBusinessId = models.IntegerField(primary_key=True, blank=False)
    businessId = models.ForeignKey(Business, on_delete=models.CASCADE, db_column="businessId")
    subBusinessName = models.CharField(max_length=100, blank=True)
    accessOf = models.CharField(max_length=100, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now_add=True)
    isDeleted = models.BooleanField(default=False)
    deletedAt = models.DateTimeField(blank=True, null=True)
