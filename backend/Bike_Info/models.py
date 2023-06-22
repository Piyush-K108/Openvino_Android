from django.db import models
import numpy as np
from django.contrib.auth import get_user_model


user = get_user_model()


def random_bike():
        return "B_" + str(np.random.randint(1,1000))
class Bike_Info(models.Model):
    def FileName(instance,filename):
        return '/'.join(['images',str(instance.Name),filename])
    b_id             = models.CharField(max_length=255 ,primary_key=True,default=random_bike)
    Electrical       = models.BooleanField(default= False)
    KM               = models.BigIntegerField(null = False)
    Condition        = models.BooleanField(default= True)
    Pic_after        = models.ImageField(upload_to = FileName,null = True)
    Pic_before       = models.ImageField(upload_to = FileName,null = True)
    Estimated_Amount = models.BigIntegerField(null =True)
    Exact_Amount     = models.BigIntegerField(null =True)
    Payed            = models.BooleanField(default= False)
    Mode_of_Payment  = models.CharField(max_length=255,null  = True)
    Time_Taken       =  models.TimeField(null=True,blank=True)
    Time_Return      =  models.TimeField(null=True,blank=True)
    class Meta:
        db_table = 'Bike_Info'
    def __str__(self):
        return self.b_id
    


class Rental(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    bike = models.ForeignKey(Bike_Info, on_delete=models.CASCADE)
    rental_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True)
    class Meta:
        db_table = 'Rental'
    def __str__(self):
        return f'Rental {self.pk}: {self.user} - {self.bike}'