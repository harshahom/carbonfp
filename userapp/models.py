from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set', blank=True)


    def __str__(self):
        return self.email

class Fuel_used(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fuel_used')
    entry_date = models.DateField(default=timezone.now)
    electricity = models.IntegerField(null=True, blank=True)
    petrol = models.IntegerField(null=True, blank=True)
    diesel = models.IntegerField(null=True, blank=True)
    total_emission = models.FloatField(null=True, blank=True)

    def calculate_total_carbon_emissions(self):
        total_emission = 0.0

        if self.electricity is not None:
            total_emission += self.electricity * 0.85

        if self.petrol is not None:
            total_emission += self.petrol * 2.296

        if self.diesel is not None:
            total_emission += self.diesel * 2.68

        return total_emission

    def save(self, *args, **kwargs):
        self.total_emission = self.calculate_total_carbon_emissions()
        super(Fuel_used, self).save(*args, **kwargs)

class Profile(models.Model):
    owner = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile_data')
    gender = models.CharField(
        max_length=20,
        choices=(
            ('male', 'Male'),
            ('female', 'Female'),
            ('others', 'Others')
        ),
        default='male',
        null=False,
        blank=False
    )
    dob = models.DateField(null=True, blank=True, default=None)
    phone = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.ImageField(upload_to="profile_image", null=True, blank=True)
    total_carbon_emissions = models.FloatField(null=True, blank=True)

    def get_total_emissions(self):
        user_fuel_used = Fuel_used.objects.filter(owner=self.owner)
        total_emissions = sum(fuel_entry.calculate_total_carbon_emissions() for fuel_entry in user_fuel_used)
        self.total_carbon_emissions = total_emissions
        self.save()
        return total_emissions


class DailyFoodChoice(models.Model): 
    FOOD_CHOICES = ( 
        ('vegetarian', 'Vegetarian'), 
        ('non_vegetarian', 'Non-Vegetarian'), 
        ('ovo_vegetarian', 'Ovo-Vegetarian'), 
    ) 

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_food_choices') 
    entry_date = models.DateField(default=timezone.now().date()) 
    food_type = models.CharField(max_length=20, choices=FOOD_CHOICES) 
    total_food_emission = models.FloatField(null=True, blank=True) 

    def calculate_total_food_emission(self): 
        if self.food_type == 'vegetarian': 
            return 723.7 
        elif self.food_type == 'non_vegetarian': 
            return 1302.66 
        elif self.food_type == 'ovo_vegetarian': 
            return 1085.55 
        else: 
            return 0.0 

    def save(self, *args, **kwargs): 
        self.total_food_emission = self.calculate_total_food_emission() 
        super(DailyFoodChoice, self).save(*args, **kwargs) 



class DailyStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_opened_at = models.DateTimeField(null=True, blank=True)
    current_streak = models.PositiveIntegerField(default=0)

    def update_streak(self):
        today = timezone.now().date()
        
        if not self.last_opened_at or self.last_opened_at.date() < today:
            # User opened the app today, update the streak
            self.current_streak += 1
        else:
            # User already opened the app today, reset streak
            self.current_streak = 1

        self.last_opened_at = timezone.now()
        self.save()