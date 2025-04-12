from commons import utils
from rest_framework import serializers
from .models import (
    Sells,
    SellsDetails
)


class SellsSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = Sells
        fields = ['code', 'date', 'description', 'created_at']

    def validate_code(self, value):
        header_code = self.context.get('header_code', None)
        if header_code and value != header_code:
            raise serializers.ValidationError('header code dan body request purchase code tidak sesuai')
        
        if not header_code and Sells.objects.filter(code=value).exists():
            raise serializers.ValidationError('Code already exist')
        
        return value
    
    #convert object model to reprentation dict
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = utils.convert_date(representation['created_at'])
        return representation
    

class SellsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellsDetails
        fields = ['item_code', 'quantity', 'header_code']

    def validate(self, attrs):
        item = attrs.get('item_code')
        sell = attrs.get('header_code')
        quantity = attrs.get('quantity')
        header_code = self.context.get('header_code', None)

        if header_code != sell.code:
            raise serializers.ValidationError('header code dan body request purchase code tidak sesuai')
        
        if item.is_deleted:
            raise serializers.ValidationError('Item code tidak ditemukan atau sudah dihapus')
        
        if quantity > item.stock:
            raise serializers.ValidationError('Stock tidak mencukupi')
        
        return attrs