from commons import utils
from rest_framework import serializers
from .models import (
    Purchases,
    PurchasesDetail
)


class PurchaseSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = Purchases
        fields = ['code', 'date', 'description', 'created_at']

    def validate_code(self, value):
        header_code = self.context.get('header_code', None)
        if header_code and value != header_code:
            raise serializers.ValidationError('header code dan body request purchase code tidak sesuai')
        
        if not header_code and Purchases.objects.filter(code=value).exists():
            raise serializers.ValidationError('Code already exist')
        
        return value

    #convert object model to reprentation dict
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = utils.convert_date(representation['created_at'])
        return representation
    

class PurchaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesDetail
        fields = ['item_code', 'quantity', 'unit_price', 'header_code']

    def validate(self, attrs):
        purchases = attrs.get('header_code').code
        header_code = self.context.get('header_code', None)
        
        if purchases != header_code:
            raise serializers.ValidationError('header code dan body request purchase code tidak sesuai')
        
        if attrs.get('item_code').is_deleted:
            raise serializers.ValidationError('Item code tidak ditemukan')
        
        return attrs


class PurchaseDetailItemsSerializer(serializers.ModelSerializer):
    purchasesdetail_set = serializers.SerializerMethodField()

    def get_purchasesdetail_set(self, obj):
        purchases = obj.purchasesdetail_set.filter(is_deleted=False).order_by('created_at')
        serializer = PurchaseDetailSerializer(purchases, many=True)
        return serializer.data
    
    class Meta:
        model = Purchases
        fields = ['code', 'date', 'description', 'purchasesdetail_set']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        purchase_detail = representation.pop('purchasesdetail_set')
        representation['details'] = purchase_detail
        return representation

