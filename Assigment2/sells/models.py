from django.db import models
from commons.models import BaseModel
from items.models import Items


class Sells(BaseModel):
    code = models.CharField(max_length=10, primary_key=True)
    date = models.DateField(auto_now_add=True)
    description = models.TextField()

    class Meta:
        db_table = 'tbl_sells'

class SellsDetails(BaseModel):
    item_code = models.ForeignKey(Items, on_delete=models.CASCADE, db_column='item_code')
    quantity = models.PositiveIntegerField()
    header_code = models.ForeignKey(Sells, on_delete=models.CASCADE, db_column='header_code')

    class Meta:
        db_table = 'tbl_sells_dtl'
