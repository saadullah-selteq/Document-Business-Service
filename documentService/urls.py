from django.urls import path
from documentService import views

urlpatterns = [
    path('pb/createFolder/', views.CreateFolder.as_view()),
    path('pb/uploadFile/', views.uploadFile.as_view()),
    path('pb/getSingleFile/', views.singlefile.as_view()),
    path('pb/getFileFolder/', views.filesfolders.as_view()),
    path('pb/RecycleBin/', views.emptyrecyclebin.as_view()),
    path('pb/emptyConatiner/', views.emptyconatiner.as_view()),
    path('pb/userRoot/', views.userroot.as_view()),
    path('pb/userDetails/', views.userdetails.as_view()),
    # path('uploadFileToFolder/', views.UploadFileToFolder.as_view()),
]
