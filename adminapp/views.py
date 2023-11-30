# adminapp/views.py
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from rest_framework import generics, permissions
import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EmissionReductionTip,CustomAdminUser
from .serializers import EmissionReductionTipSerializer
from django.contrib.auth.models import User



@csrf_exempt
@require_POST
def admin_login(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'username' not in data or 'password' not in data:
        return JsonResponse({'error': 'Username and password are required'}, status=400)

    username = data['username']
    password = data['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return JsonResponse({'message': 'Login successful', 'access_token': access_token}, status=200)
    else:
        return JsonResponse({'error': 'Invalid username or password'}, status=401)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def admin_profile(request):
    if request.method == 'GET':
        admin_data = {
            'username': request.user.username,
            'email': request.user.email,
        }
        return Response(admin_data)
    elif request.method == 'PUT':
        request.user.username = request.data.get('username', request.user.username)
        request.user.email = request.data.get('email', request.user.email)
        request.user.save()
        return Response({'message': 'Admin profile updated successfully'})


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