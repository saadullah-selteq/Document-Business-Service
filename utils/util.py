import io
import re
import hashlib
from datetime import datetime, timedelta
# from PIL import Image
import subprocess
from azure.storage.blob import BlobServiceClient
from django.conf import settings

from datetime import datetime
import pytz


def convert_to_timezone(datetime_str, target_timezone):
    # Parse the datetime string
    utc_dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

    # Set the timezone to UTC
    # utc_dt = utc_dt.replace(tzinfo=pytz.UTC)

    # Convert to the target timezone
    target_tz = pytz.timezone(target_timezone)
    target_dt = utc_dt.astimezone(target_tz)

    return target_dt


package_list = [
    {
        "type": "Basic",
        "storageLimit": "10",
        "duration": "1 month",
    },
    {
        "type": "Medium",
        "storageLimit": "50",
        "duration": "6 month",
    },
    {
        "type": "Premium",
        "storageLimit": "100",
        "duration": "1 Year",
    }
]


def containerClient():
    blob_service_client = BlobServiceClient(
        account_url=settings.BLOB_ACCOUNT_URL,
        credential=settings.BLOB_SAS_TOKEN
    )
    container_client = blob_service_client.get_container_client(settings.CONTAINER_NAME)
    return container_client


def md5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def last_month_regex():
    today = datetime.today()
    return re.compile((today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-'))


def last_day_regex():
    today = datetime.today()
    return re.compile((today - timedelta(days=1)).strftime('%Y-%m-%sd'))


def validate_page_number(page):
    try:
        return abs(int(page))

    except ValueError:
        return 1


def get_package(package_type):
    for package in package_list:
        if package['type'] == package_type:
            return package
    return "Not found"


def get_package_date(package_type):
    today = datetime.now()
    if package_type == "1 month":
        expirationDate = today + timedelta(days=30)
        return expirationDate
    elif package_type == "6 month":
        expirationDate = today + timedelta(days=30 * 6)
        return expirationDate
    elif package_type == "1 Year":
        expirationDate = today + timedelta(days=365)
        return expirationDate


def normalizeText(text: str) -> str:
    if text is not None:
        text = text.replace('’', "'").replace("\n", "").replace("‘", "'")
        return text

# def compress_media_file(file, output_format=None):
#     file_extension = file[0].name.split(".")[-1]
#     if file_extension in ["jpg", "jpeg", "png", "gif"]:
#         if file_extension in ['jpg', 'jpeg']:
#             output_format = 'JPEG'
#         elif file_extension in ['png']:
#             output_format = 'PNG'

#         fp = io.BytesIO()
#         image = Image.open([0])
#         image.save(fp, format=output_format, optimize=True, quality=85)
#         fp.seek(0)
#         return fp


# from django.http import StreamingHttpResponse

# def some_view(request):
#     file = open("large_file.mp4", "rb")
#     response = StreamingHttpResponse(file)
#     response['Content-Type'] = 'video/mp4'
#     return response

# from django.http import FileResponse

# def some_view(request):
#     file = open("example.pdf", "rb")
#     response = FileResponse(file)
#     response['Content-Type'] = 'application/pdf'
#     return response

# import ftplib
# from django.http import FileResponse

# def some_view(request):
#     ftp = ftplib.FTP("ftp.example.com")
#     ftp.login("username", "password")
#     ftp.cwd("/path/to/file")
#     file = io.BytesIO()
#     ftp.retrbinary("RETR file.pdf", file.write)
#     ftp.quit()
#     file.seek(0)
#     response = FileResponse(file)
#     response['Content-Type'] = 'application/pdf'
#     return response
