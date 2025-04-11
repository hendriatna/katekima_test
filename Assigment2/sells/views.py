from django.db import transaction
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from commons.constants import ResultMessage as message
from commons.headerresponse import ResultResponse as response
from items.models import Items
from purchases.models import PurchasesDetail
from purchases.serializers import PurchaseDetailItemsSerializer
from .models import Sells
from .serializers import (
    SellsSerializer,
    SellsDetailSerializer,
    SellsDetailItemsSerializer,
)


class SellsView(APIView):
    def get(self, request):
        try:
            sells = Sells.objects.filter(is_deleted=False).order_by('created_at')
            serializer = SellsSerializer(sells, many=True)
            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

    def post(self, request):
        request_data = request.data
        try:
            with transaction.atomic():
                serializer = SellsSerializer(data=request_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                
                return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except ValidationError as e:
            #return error message from validation in serializer
            return response.to_json(message.INPUT_ERROR, e)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

class SellsDetailView(APIView):
    def get(self, request, code):
        try:
            sell = Sells.objects.get(code=code, is_deleted=False)
            serializer = SellsSerializer(sell)
            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Sells.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)

        
    def put(self, request, code):
        request_data = request.data
        try:
            with transaction.atomic():
                sell = Sells.objects.get(code=code, is_deleted=False)
                serializer = SellsSerializer(sell, data=request_data, context={'header_code':code})
                #check the data request is valid or not, if not valid will except on ValidationError
                if serializer.is_valid(raise_exception=True):
                    #save data
                    serializer.save()

                return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except Sells.DoesNotExist:
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
                sell = Sells.objects.get(code=code, is_deleted=False)
                sell.is_deleted = True
                sell.save()
                return response.to_json(message.DELETED_SUCCESS_RESPONSE)
        except Sells.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

class SellsDetailHeaderView(APIView):
    def get(self, request, header_code):
        try:
            purchase = Sells.objects.prefetch_related('sellsdetails_set').get(code=header_code, is_deleted=False)
            serliazer = SellsDetailItemsSerializer(purchase)

            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serliazer.data)
        except Sells.DoesNotExist:
            #return error data not exist if item by code is none
            return response.to_json(message.NOT_FOUND_ERROR)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

    def post(self, request, header_code):
        request_data = request.data
        try:
            if not Sells.objects.filter(code=header_code, is_deleted=False).exists():
                return response.to_json(message.NOT_FOUND_ERROR)
            
            serializer = SellsDetailSerializer(data=request_data, context={'header_code':header_code})
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            item = Items.objects.get(code=serializer.data['item_code'])
            purchases_item = PurchasesDetail.objects.filter(item_code=item).order_by('-created_at')
            
            item_stock = item.stock
            purchase_available = []
            
            for purchase in purchases_item:
                if purchase.quantity <= item_stock:
                    purchase_available.append(purchase)
                    item_stock -= purchase.quantity
                else:
                    purchase.quantity = item_stock
                    purchase_available.append(purchase)
                    break

            sell_amount = 0
            quantity_sell = serializer.data['quantity']
            purchase_available.reverse()
            for purchase in purchase_available:
                if purchase.quantity >= quantity_sell:
                    sell_amount += purchase.unit_price * quantity_sell
                    break
                else:
                    sell_amount += purchase.unit_price * purchase.quantity
                    quantity_sell = quantity_sell - purchase.quantity

            item.stock -= serializer.data['quantity']
            item.balance -= sell_amount
            item.save()
            
            return response.to_json(message.GENERAL_SUCCESS_RESPONSE, serializer.data)
        except ValidationError as e:
            #return error message from validation in serializer
            return response.to_json(message.INPUT_ERROR, e)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)