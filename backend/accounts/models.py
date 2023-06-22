from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import numpy as np
def random_id():
        return "U_" + str(np.random.randint(1000,9000)) 
class UserAccountManager(BaseUserManager):
    def create_user(self, phone, password=None):
        if not phone:
            raise ValueError("User must have a phone number")
        user = self.model(phone=phone)
        user.set_password(password)
        user.save()
        return user
    
    def create_teamuser(self, name , phone, password,**extra_fields):
      
        if not (phone):
            raise ValueError("User must have a phone ")
        
        phone = phone
        name = name
        password = password
        user = self.model(phone=phone,name = name,is_staff=True,password=password)
        user.save()

        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
       
        return self._create_user(phone, password, **extra_fields)

    def _create_user(self, phone, password=None, **extra_fields):
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user



class UserAccounts(AbstractBaseUser, PermissionsMixin):
    def FileName(instance, filename):
        return '/'.join(['images', str(instance.name), filename])
    uid = models.CharField(max_length=255,primary_key=True,default=random_id)
    name = models.CharField(max_length=255,null=True)
    phone = models.CharField(max_length=20, unique=True,null =False)
    email = models.CharField(max_length=255,unique=True,null=True)
    Country = models.CharField(max_length=255,null =True)
    otp = models.CharField(max_length=6,null=True)
    State = models.CharField(max_length=255,null =True)
    City = models.CharField(max_length=255,null =True)
    Date_of_Birth = models.DateField(null =True)
    ProfilePic = models.ImageField(upload_to=FileName, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'

    objects = UserAccountManager()

    def get_full_name(self):
        return self.phone

    def get_short_name(self):
        return self.phone

    def __str__(self):
        return self.phone
