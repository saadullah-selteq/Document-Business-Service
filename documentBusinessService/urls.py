from django.urls import path
from documentBusinessService.views.BusinessView import CreateBusiness
from documentBusinessService.views.SubBusinessView import CreateSubBusiness
from documentBusinessService.views.SubBusinessView import getSubBusinessDetails
from documentBusinessService.views.BusinessFolderView import CreateBusinessFolder
from documentBusinessService.views.BusinessFileView import UploadBusinessFiles
from documentBusinessService.views.RecyclebinView import emptyrecyclebinbusiness
from documentBusinessService.views.BusinessFileView import UploadSubBusinessFiles
from documentBusinessService.views.BusinessFileView import  singlefile
from documentBusinessService.views.BusinessFolderView import filesfolders
from  documentBusinessService.views.BusinessFolderView import CreateSubBusinessFolder

urlpatterns = [
    path('createBusiness/', CreateBusiness.as_view()),
    path('createSubBusiness/', CreateSubBusiness.as_view()),
    path('subBusinessDetails/',getSubBusinessDetails.as_view()),
    path('createBusinessFolder/',CreateBusinessFolder.as_view()),
    path('uploadBusinessFile/', UploadBusinessFiles.as_view()),
    path('getSingleFile/',singlefile.as_view()),
    path('getFileFolder/', filesfolders.as_view()),
    path('createSubBusinessFolder/',CreateSubBusinessFolder.as_view()),
    path('uploadSubBusinessFile/',UploadSubBusinessFiles.as_view()),
    path('RecycleBinBusiness/',emptyrecyclebinbusiness.as_view()),
]