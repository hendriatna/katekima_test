import json
from rest_framework import status
from json import JSONEncoder
from commons.constants import ResultMessage
from django.http.response import JsonResponse



class ResultResponse:
    def __init__(self, resultmassage, data, total_row, param, keyword=None):
        result = ResultMessage(resultmassage)
        self.status = result.success
        self.code = result.code
        self.message = result.message
        self.data = data

    def to_json(message, data=None, count_row=None, param=None):
        responseDumps = json.dumps(ResultResponse(message, data, count_row, param), indent=4, cls=ResponseEncoder)
        responseLoads = json.loads(responseDumps)
        return JsonResponse(responseLoads, status=status.HTTP_200_OK, safe=False)


class ResponseDataEncoder(JSONEncoder):
    def default(self, o):
            return o.__dict__
    
    
class ResponseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__