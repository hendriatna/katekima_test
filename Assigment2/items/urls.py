from django.urls import path
from .views import (
    ItemsView,
    ItemsDetailView
    )

urlpatterns = [
    path('items/', ItemsView.as_view(), name='list-items'),
    path('items/<str:code>', ItemsDetailView.as_view(), name='items-detail'),
]