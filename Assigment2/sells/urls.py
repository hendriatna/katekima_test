from django.urls import path
from .views import (
    SellsView,
    SellsDetailView,
    SellsDetailHeaderView
)

urlpatterns = [
    path('sell/', SellsView.as_view(), name='list-sells'),
    path('sell/<str:code>', SellsDetailView.as_view(), name='sells-detail'),
    path('sell/<str:header_code>/details', SellsDetailHeaderView.as_view(), name='sells-detail'),
]