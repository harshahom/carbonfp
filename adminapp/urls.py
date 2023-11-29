from django.urls import path
from .views import (admin_register, admin_verify_otp, admin_resend_otp,EmissionReductionTipListView
,EmissionReductionTipDetailView)

urlpatterns = [
    path('admin-register/', admin_register, name='admin-register'),
    path('admin-verify-otp/', admin_verify_otp, name='admin-verify-otp'),
    path('admin-resend-otp/', admin_resend_otp, name='admin-resend-otp'),
    path('emission-tips/', EmissionReductionTipListView.as_view(), name='emission-tip-list'),
    path('emission-tips/detail/', EmissionReductionTipDetailView.as_view(), name='emission-tip-detail'),
]
