from django.test import TestCase
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (register, verify_otp,resend_otp,ProfileListView,ProfileDetailView,FuelUsedListView,FuelUsedDetailView
,EmissionRecordView,DailyFoodChoiceListView,DailyFoodChoiceDetailView, DailyStreakAPIView)

urlpatterns = [
    path('register/', register, name='register_user'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('user/resend-otp/', resend_otp, name='resend_otp'),
    path('profiles/', ProfileListView.as_view(), name='profile-list'),
    path('profiles/detail/', ProfileDetailView.as_view(), name='profile-detail'),
    path('fuel-used/', FuelUsedListView.as_view(), name='fuel-used-list'),
    path('fuel-used/detail/', FuelUsedDetailView.as_view(), name='fuel-used-detail'),
    path('emission-record/', EmissionRecordView.as_view(), name='emission-record'),
    path('daily-food-choices/', DailyFoodChoiceListView.as_view(), name='daily-food-choices-list'), 
    path('daily-food-choices/detail/', DailyFoodChoiceDetailView.as_view(), name='daily-food-choices-detail'),
    path('daily-streak/', DailyStreakAPIView.as_view(), name='get_daily_streak'), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
