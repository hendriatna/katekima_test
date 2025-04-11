from django.db import models
from commons.models import BaseModel


class Items(BaseModel):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=5)
    description = models.TextField()
    stock = models.BigIntegerField(default=0)
    balance = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'tbl_items'
