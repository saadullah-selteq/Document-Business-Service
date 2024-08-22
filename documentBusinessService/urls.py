from django.urls import path, include
from documentBusinessService.views.BusinessManagement import BusinessViewSet
from documentBusinessService.views.BusinessManagement import CreateSubBusiness
from documentBusinessService.views.BusinessManagement import getSubBusinessDetails
from documentBusinessService.views.FileFolderManagement import CreateBusinessFolder
from documentBusinessService.views.FileFolderManagement import UploadBusinessFiles
from documentBusinessService.views.RecyclebinView import emptyrecyclebinbusiness
from documentBusinessService.views.FileFolderManagement import UploadSubBusinessFiles
from documentBusinessService.views.FileFolderManagement import SingleFile
from documentBusinessService.views.FileFolderManagement import FilesFolders
from documentBusinessService.views.FileFolderManagement import CreateSubBusinessFolder
from documentBusinessService.views.BusinessManagement import BusinessViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet, basename='business')
urlpatterns = [
    path('', include(router.urls)),
    path('createSubBusiness/', CreateSubBusiness.as_view()),
    path('createSubBusiness/', CreateSubBusiness.as_view()),
    path('subBusinessDetails/', getSubBusinessDetails.as_view()),
    path('createBusinessFolder/', CreateBusinessFolder.as_view()),
    path('uploadBusinessFile/', UploadBusinessFiles.as_view()),
    path('getSingleFile/', SingleFile.as_view()),
    path('getFileFolder/', FilesFolders.as_view()),
    path('createSubBusinessFolder/', CreateSubBusinessFolder.as_view()),
    path('uploadSubBusinessFile/', UploadSubBusinessFiles.as_view()),
    path('RecycleBinBusiness/', emptyrecyclebinbusiness.as_view()),
]
