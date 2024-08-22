import traceback
from msrest.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from documentBusinessService import service
from utils.responses import conflict, internal_server_error, bad_request, created, ok


class userroot(APIView):
    def get(self, request):
        try:
            ownerId = request.GET.get('ownerId', None)
            if ownerId is not None:
                data = service.getUserRootId(ownerId)
            return ok(data=data)

        except Exception as err:
            print(traceback.format_exc())
            return internal_server_error(message='Failed to get bookings')
