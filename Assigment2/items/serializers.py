from rest_framework import serializers
from commons import utils
from .models import Items
from commons.constants import (
    NAME_FIELD_ERRORS,
    UNIT_FIELD_ERRORS,
    DESC_FIELD_ERRORS,
)


class ItemsSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    name = serializers.CharField(max_length=100, error_messages=NAME_FIELD_ERRORS) #set message error
    unit = serializers.CharField(max_length=5, error_messages=UNIT_FIELD_ERRORS) #set message error
    description = serializers.CharField(error_messages=DESC_FIELD_ERRORS) #set message error
    
    class Meta:
        model = Items
        fields = ['code', 'name', 'unit', 'description', 'stock', 'balance', 'created_at']

    def validate_code(self, value):
        header_code = self.context.get('header_code', None)
        if header_code and value != header_code:
            raise serializers.ValidationError('header code dan body request purchase code tidak sesuai')
        
        if not header_code and Items.objects.filter(code=value).exists():
            raise serializers.ValidationError('Code already exist')
        
        return value
    
    #convert object model to reprentation dict
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = utils.convert_date(representation['created_at'])
        return representation