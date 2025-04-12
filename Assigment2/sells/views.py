from django.db import transaction
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from commons.constants import ResultMessage as message
from commons.headerresponse import ResultResponse as response
from django.db.models import Sum
from items.models import Items
from purchases.models import PurchasesDetail
from .models import Sells, SellsDetails
from .serializers import (
    SellsSerializer,
    SellsDetailSerializer,
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
        message_resp = message.GENERAL_SUCCESS_RESPONSE
        try:
            #select sells detail by is_deleted false, header_code, is_deleted header_code false, 
            # and is_deleted item_code false order by created_at asc
            sells_detail = (SellsDetails
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
            if not sells_detail.exists():
                message_resp = message.NOT_FOUND_ISDELETED
            
            serializer = SellsDetailSerializer(sells_detail, many=True)
            return response.to_json(message_resp, serializer.data)
        except Exception as e:
            #return error general for handling other error
            return response.to_json(message.GENERAL_ERROR_RESPONSE)
        

    def post(self, request, header_code):
        request_data = request.data
        try:
            if not Sells.objects.filter(code=header_code, is_deleted=False).exists():
                return response.to_json(message.NOT_FOUND_ERROR)
            #validate data in serialize and send header_code
            serializer = SellsDetailSerializer(data=request_data, context={'header_code':header_code})
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            item = Items.objects.get(code=request_data['item_code'])
            #get purchase data by items created desc for calculation unit price
            purchases_item = PurchasesDetail.objects.filter(item_code=item).order_by('-created_at')
            
            item_stock = item.stock
            purchase_available = []
            #set sisa purchase yang masih available, dibandingkan dengan stock yang masih tersedia di items
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
            #list purchase yg sudah di filter direverse agar menjadi desc, dan siap dikurangi oleh sell
            purchase_available.reverse()
            #menhitung stock dan balance berdasarkan harga unit item yang masih tersedia
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