from django.urls import path
from .views import (
    PurchasesView,
    PurchaseDetailView,
    PurchaseDetailHeaderView
)

urlpatterns = [
    path('purchases/', PurchasesView.as_view(), name='list-purchases'),
    path('purchases/<str:code>', PurchaseDetailView.as_view(), name='purchases-detail'),
    path('purchases/<str:header_code>/details', PurchaseDetailHeaderView.as_view(), name='purchases-detail-item'),
]