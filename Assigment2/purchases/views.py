from django.db import transaction
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from commons.constants import ResultMessage as message
from commons.headerresponse import ResultResponse as response
from items.models import Items
from .models import Purchases, PurchasesDetail
from .serializers import (
    PurchaseSerializer,
    PurchaseDetailSerializer,
)


class PurchasesView(APIView):
    def get(self, request):
        try:
            purchases = Purchases.objects.filter(is_deleted=False).order_by('created_at')
            serializer = PurchaseSerializer(purchases, many=True)
            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        
    def post(self, request):
        request_data = request.data
        try:
            with transaction.atomic():
                serializer = PurchaseSerializer(data=request_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                
                return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except ValidationError as e:
            #return error message from validation in serializer
            return response.to_json(message.INPUT_ERROR, e)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

class PurchaseDetailView(APIView):
    def get(self, request, code):
        try:
            purchase = Purchases.objects.get(code=code, is_deleted=False)
            serializer = PurchaseSerializer(purchase)
            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Purchases.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

    def put(self, request, code):
        request_data = request.data
        try:
            with transaction.atomic():
                purchase = Purchases.objects.get(code=code, is_deleted=False)
                serializer = PurchaseSerializer(purchase, data=request_data, context={'header_code':code})
                #check the data request is valid or not, if not valid will except on ValidationError
                if serializer.is_valid(raise_exception=True):
                    #save data
                    serializer.save()

                return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Purchases.DoesNotExist:
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
            with transaction.atomic():
                purchase = Purchases.objects.get(code=code, is_deleted=False)
                purchase.is_deleted = True
                purchase.save()
                return response.to_json(message.DELETED_SUCCESS_RESPONSE)
        except Purchases.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

class PurchaseDetailHeaderView(APIView):
    def get(self, request, header_code):
        message_resp = message.GENERAL_SUCCESS_RESPONSE
        try:
            #select purchase detail by is_deleted false, header_code, is_deleted header_code false, 
            # and is_deleted item_code false order by created_at asc
            purchase_detail = (
                PurchasesDetail
                .objects
                .filter(
                    is_deleted=False,
                    header_code__code=header_code,
                    header_code__is_deleted=False,
                    item_code__is_deleted=False
                )
                .order_by('created_at')
            )
            #if data not exist, set message not found
            if not purchase_detail.exists():
                message_resp = message.NOT_FOUND_ISDELETED

            serliazer = PurchaseDetailSerializer(purchase_detail, many=True)
            return response.to_json(message_resp, serliazer.data)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)


    def post(self, request, header_code):
        request_data = request.data
        try:
            with transaction.atomic():
                if not Purchases.objects.filter(code=header_code, is_deleted=False).exists():
                    return response.to_json(message.NOT_FOUND_ERROR)
                #validate data in serialize and send header_code
                serializer = PurchaseDetailSerializer(data=request_data, context={'header_code':header_code})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                #update stock and balance items
                item = Items.objects.get(code=request_data['item_code'])
                item.stock = item.stock + serializer.data['quantity']
                item.balance = item.balance + (serializer.data['unit_price'] * serializer.data['quantity'])
                item.save()

            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except ValidationError as e:
            #return error message from validation in serializer
            return response.to_json(message.INPUT_ERROR, e)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)