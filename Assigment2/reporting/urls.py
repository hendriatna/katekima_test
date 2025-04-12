from django.urls import path
from .views import StockReportPDFView

urlpatterns = [
    path('report/<str:item_code>', StockReportPDFView.as_view(), name='list-sells'),
]