from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models

class CustomAdminUser(AbstractUser):
    groups = models.ManyToManyField('auth.Group', related_name='admin_custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='admin_custom_user_set', blank=True)

class EmissionReductionTip(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='emission_reduction_tips')
    tip_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Tip - {self.created_at}"
