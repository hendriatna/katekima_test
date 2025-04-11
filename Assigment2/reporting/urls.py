from django.urls import path
from .views import StockReportPDFView

urlpatterns = [
    path('stock-report/', StockReportPDFView.as_view(), name='list-sells'),
]