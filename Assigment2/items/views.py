from .models import Items
from django.db import transaction
from rest_framework.views import APIView
from .serializers import ItemsSerializer
from rest_framework.exceptions import ValidationError
from commons.constants import ResultMessage as message
from commons.headerresponse import ResultResponse as response

# this for API items
# all request can you access in file testing.rest

class ItemsView(APIView):
    def get(self, request):
        try :
            #get all data items where is_deleted is false, and order by created_at desc
            items = Items.objects.filter(is_deleted=False).order_by('created_at')

            #convert data list item to serializer, many=true for set many data
            serializer = ItemsSerializer(items, many=True)

            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

    def post(self, request):
        request_data = request.data
        try:
            #rolback data if have any error exception
            with transaction.atomic():
                #process data request in serializer, for check validation field
                serializer = ItemsSerializer(data=request_data)

                #check the data request is valid or not, if not valid will except on ValidationError
                if serializer.is_valid(raise_exception=True):

                    #save data
                    serializer.save()

            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except ValidationError as e:
            #return error message from validation in serializer
            return response.to_json(message.INPUT_ERROR, e)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

class ItemsDetailView(APIView):
    def get(self, request, code):
        try:
            #get data by code
            item = Items.objects.get(code=code, is_deleted=False)

            #convert data for representaion in serializer
            serializer = ItemsSerializer(item)

            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Items.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        
        
    def put(self, request, code):
        request_data = request.data
        try:
            #rolback data if have any error exception
            with transaction.atomic():
                #get data by code and is_deleted = false
                item = Items.objects.get(code=code, is_deleted=False)

                #process data request for update
                serializer = ItemsSerializer(item, data=request_data, context={'header_code':code})

                #check the data request is valid or not, if not valid will except on ValidationError
                if serializer.is_valid(raise_exception=True):

                    #save data
                    serializer.save()

                return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Items.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        except ValidationError as e:
            #return error message from validation in serializer
            return response.to_json(message.INPUT_ERROR, e)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

    def delete(self, request, code):
        try:
            #rolback data if have any error exception
            with transaction.atomic():
                #get data item by code and is_deleted = false
                item = Items.objects.get(code=code, is_deleted=False)

                #set is_deleted = True, and save the data
                item.is_deleted = True
                item.save()

                return response.to_json(message.DELETED_SUCCESS_RESPONSE)
        except Items.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)