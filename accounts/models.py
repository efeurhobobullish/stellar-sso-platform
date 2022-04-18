from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class StellarResource(models.Model):
    user = models.OneToOneField(User, null = True, blank = True, on_delete = models.CASCADE)
    acc_ID = models.CharField(max_length = 250, blank=True)
    secretkey = models.CharField(max_length = 250, blank=True)
    has_account = models.BooleanField(default= False)
    date_created = models.DateTimeField(auto_now_add=True, null = True)

    def __str__(self):
        return f"{self.user.username.upper()} - {self.user.email}"