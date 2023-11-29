# adminapp/views.py
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from rest_framework import generics, permissions
import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EmissionReductionTip
from .serializers import EmissionReductionTipSerializer

AdminUser = get_user_model()

@csrf_exempt
@require_POST
def admin_register(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'email' not in data:
        return JsonResponse({'error': 'Email address is required'}, status=400)

    email = data['email']
    otp = get_random_string(length=6, allowed_chars='0123456789')

    cache.set(email, otp, timeout=300)
    username = email.split('@')[0]
    admin_user = AdminUser(username=username, email=email)

    subject = 'Admin Registration OTP'
    message = f'Your OTP for admin registration is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        admin_user.save()
        send_mail(subject, message, from_email, recipient_list)
        return JsonResponse({'message': 'OTP sent successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Error saving admin user or sending email: {str(e)}'}, status=500)

AdminUser = get_user_model()

@csrf_exempt
@require_POST
def admin_verify_otp(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'email' not in data or 'otp' not in data:
        return JsonResponse({'error': 'Email and OTP are required'}, status=400)

    email = data['email']
    admin_user_entered_otp = data['otp']
    stored_otp = cache.get(email)

    if stored_otp is None:
        return JsonResponse({'error': 'OTP expired or not found. Please request a new OTP.'}, status=400)

    admin_user = AdminUser.objects.filter(email=email).first()

    if admin_user and admin_user_entered_otp == stored_otp:
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        return JsonResponse({'message': 'OTP verified successfully', 'access_token': access_token}, status=200)
    else:
        return JsonResponse({'error': 'Invalid OTP'}, status=400)

@csrf_exempt
@require_POST
def admin_resend_otp(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'email' not in data:
        return JsonResponse({'error': 'Email address is required'}, status=400)

    email = data['email']
    admin_user = AdminUser.objects.filter(email=email).first()

    if admin_user is None:
        return JsonResponse({'error': 'Admin user not found with the provided email'}, status=404)

    new_otp = get_random_string(length=6, allowed_chars='0123456789')
    cache.set(email, new_otp, timeout=300)
    subject = 'Admin Registration OTP'
    message = f'Your new OTP for admin registration is: {new_otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return JsonResponse({'message': 'New OTP sent successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Error sending email: {str(e)}'}, status=500)
    
class EmissionReductionTipListView(generics.ListCreateAPIView):
    queryset = EmissionReductionTip.objects.all()
    serializer_class = EmissionReductionTipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EmissionReductionTipDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmissionReductionTip.objects.all()
    serializer_class = EmissionReductionTipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            tip_id = self.request.data.get('id')
            return EmissionReductionTip.objects.get(id=tip_id, user=self.request.user)
        except EmissionReductionTip.DoesNotExist:
            raise Http404

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"detail": "Tip updated successfully."})

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Tip deleted successfully."}, status=status.HTTP_204_NO_CONTENT)