from django.urls import path
from .views import (admin_login,admin_profile,EmissionReductionTipListView
,EmissionReductionTipDetailView)

urlpatterns = [
    path('admin-login/', admin_login, name='admin-login'),
    path('admin-profile/', admin_profile, name='admin-profile'),
    path('emission-tips/', EmissionReductionTipListView.as_view(), name='emission-tip-list'),
    path('emission-tips/detail/', EmissionReductionTipDetailView.as_view(), name='emission-tip-detail'),
]
