from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from adminapp.models import EmissionReductionTip
from adminapp.serializers import EmissionReductionTipSerializer
from .models import Profile,Fuel_used,DailyFoodChoice, DailyStreak
from .serializers import ProfileSerializer, Fuel_usedSerializer,DailyFoodChoiceSerializer, DailyStreakSerializer
from django.contrib.auth.models import User
from django.db import IntegrityError

@csrf_exempt
@require_POST
def register(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'email' not in data:
        return JsonResponse({'error': 'Email address is required'}, status=400)

    email = data['email']
    otp = get_random_string(length=6, allowed_chars='0123456789')

    cache.set(email, otp, timeout=300)
    username = email.split('@')[0]
    user = User(username=username, email=email)

    subject = 'Registration OTP'
    message = f'Your OTP for registration is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        user.save()
        send_mail(subject, message, from_email, recipient_list)
        return JsonResponse({'message': 'OTP sent successfully'}, status=200)
    except IntegrityError:
        return JsonResponse({'error': 'Username or email already exists. Please try again.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error saving user or sending email: {str(e)}'}, status=500)

    

User = get_user_model()

@csrf_exempt
@require_POST
def verify_otp(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'email' not in data or 'otp' not in data:
        return JsonResponse({'error': 'Email and OTP are required'}, status=400)

    email = data['email']
    user_entered_otp = data['otp']
    stored_otp = cache.get(email)

    if stored_otp is None:
        return JsonResponse({'error': 'OTP expired or not found. Please request a new OTP.'}, status=400)
    if user_entered_otp == stored_otp:
        user, created = User.objects.get_or_create(email=email)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return JsonResponse({'message': 'OTP verified successfully', 'access_token': access_token}, status=200)
    else:
        return JsonResponse({'error': 'Invalid OTP'}, status=400)
    
@csrf_exempt
@require_POST
def resend_otp(request):
    data = json.loads(request.body.decode('utf-8'))

    if 'email' not in data:
        return JsonResponse({'error': 'Email address is required'}, status=400)

    email = data['email']
    user = User.objects.filter(email=email).first()

    if user is None:
        return JsonResponse({'error': 'User not found with the provided email'}, status=404)
    new_otp = get_random_string(length=6, allowed_chars='0123456789')
    cache.set(email, new_otp, timeout=300)
    subject = 'Registration OTP'
    message = f'Your new OTP for registration is: {new_otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return JsonResponse({'message': 'New OTP sent successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Error sending email: {str(e)}'}, status=500)



class FuelUsedListView(generics.ListCreateAPIView):
    serializer_class = Fuel_usedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Fuel_used.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)
        fuel_entry = serializer.instance
        fuel_entry.total_emission = fuel_entry.calculate_total_carbon_emissions()
        fuel_entry.save()

        return Response({"detail": "Fuel used data added successfully for the current month."}, status=status.HTTP_201_CREATED)


class FuelUsedDetailView(APIView):
    serializer_class = Fuel_usedSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        month = request.data.get('month', timezone.now().month)

        try:
            fuel_entries = Fuel_used.objects.filter(
                owner=user_id,
                entry_date__month=month
            )
            serializer = Fuel_usedSerializer(fuel_entries, many=True)
            return Response(serializer.data)
        except Fuel_used.DoesNotExist:
            return Response({"detail": "Fuel used detail does not exist for the provided user and month."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        fuel_entry = Fuel_used.objects.get(owner=user_id)
        serializer = Fuel_usedSerializer(fuel_entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        fuel_entry = Fuel_used.objects.get(owner=user_id)
        fuel_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileListView(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ProfileDetailView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        profile = Profile.objects.get(owner=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        profile = Profile.objects.get(owner=user_id)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_id = request.data.get('user_id', self.request.user.id)
        profile = Profile.objects.get(owner=user_id)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmissionRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        current_month_entries = Fuel_used.objects.filter(
            owner=current_user,
            entry_date__range=[current_month_start, current_month_start.replace(month=current_month_start.month + 1) - timedelta(microseconds=1)]
        )

        current_month_emissions = sum(entry.calculate_total_carbon_emissions() for entry in current_month_entries)

        current_month_food_choices = DailyFoodChoice.objects.filter(
            owner=current_user,
            entry_date__range=[current_month_start, current_month_start.replace(month=current_month_start.month + 1) - timedelta(microseconds=1)]
        )
        current_month_food_emissions = sum(food_choice.total_food_emission for food_choice in current_month_food_choices)

        current_month_emissions += current_month_food_emissions

        past_months_data = []
        for i in range(1, 6):
            start_date = current_month_start - timedelta(days=current_month_start.day)
            end_date = current_month_start - timedelta(microseconds=1)
            month_entries = Fuel_used.objects.filter(
                owner=current_user,
                entry_date__range=[start_date, end_date]
            )

            total_emissions = sum(entry.calculate_total_carbon_emissions() for entry in month_entries)

            month_food_choices = DailyFoodChoice.objects.filter(
                owner=current_user,
                entry_date__range=[start_date, end_date]
            )
            total_food_emissions = sum(food_choice.total_food_emission for food_choice in month_food_choices)

            total_emissions += total_food_emissions

            past_months_data.append({
                'month': start_date.strftime('%B %Y'),
                'total_emissions': total_emissions,
            })
            current_month_start = start_date - timedelta(days=1)

        response_data = {
            'current_month_emissions': current_month_emissions,
            'past_months_emissions': past_months_data,
        }

        return JsonResponse(response_data)



class DailyFoodChoiceListView(generics.ListCreateAPIView): 
    serializer_class = DailyFoodChoiceSerializer 
    permission_classes = [IsAuthenticated] 

    def get_queryset(self): 
        return DailyFoodChoice.objects.filter(owner=self.request.user)  
    def perform_create(self, serializer): 
        serializer.save(owner=self.request.user) 

class DailyFoodChoiceDetailView(APIView): 
    serializer_class = DailyFoodChoiceSerializer 
    permission_classes = [IsAuthenticated] 
 
    def get(self, request): 
        user_id = request.data.get('user_id', self.request.user.id) 
        entry_date = request.data.get('entry_date', timezone.now().date()) 
        food_choices = DailyFoodChoice.objects.filter(owner=user_id, entry_date=entry_date) 

        if not food_choices.exists(): 
            return Response({"detail": "Daily food choice does not exist for the provided user and date."}, 
                            status=status.HTTP_404_NOT_FOUND) 

        serializer = DailyFoodChoiceSerializer(food_choices, many=True) 
        return Response(serializer.data) 

    def put(self, request): 
        user_id = request.data.get('user_id', self.request.user.id) 
        entry_date = request.data.get('entry_date', timezone.now().date())          
        food_choices = DailyFoodChoice.objects.filter(owner=user_id, entry_date=entry_date)  

        if not food_choices.exists(): 
            return Response({"detail": "Daily food choice does not exist for the provided user and date."}, 
                            status=status.HTTP_404_NOT_FOUND) 
        food_choice = food_choices.first() 
        serializer = DailyFoodChoiceSerializer(food_choice, data=request.data) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def delete(self, request): 

        user_id = request.data.get('user_id', self.request.user.id) 
        entry_date = request.data.get('entry_date', timezone.now().date())          
        food_choices = DailyFoodChoice.objects.filter(owner=user_id, entry_date=entry_date) 

        if not food_choices.exists(): 

            return Response({"detail": "Daily food choice does not exist for the provided user and date."}, 
                            status=status.HTTP_404_NOT_FOUND) 
        food_choice = food_choices.first() 
        food_choice.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT) 
    


class DailyStreakAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            daily_streak, created = DailyStreak.objects.get_or_create(user=request.user)
            daily_streak.update_streak()
            serializer = DailyStreakSerializer(daily_streak)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AllEmissionReductionTipsView(generics.ListAPIView):
    queryset = EmissionReductionTip.objects.all()
    serializer_class = EmissionReductionTipSerializer
