from django.contrib.auth import get_user_model
from django.db import models


class Address(models.Model):
    address = models.CharField(max_length=256)
    detail_address = models.CharField(max_length=256)
    zone_code = models.CharField(max_length=32)


class StudentProfile(models.Model):
    user = models.ForeignKey(
        to=get_user_model(), related_name='student_profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    image = models.ImageField(default='default_profile.png')
    birthdate = models.DateField()
    phone = models.CharField(max_length=64)
    email = models.CharField(max_length=256)
    address = models.ForeignKey(to=Address, on_delete=models.CASCADE)


class CarerProfile(models.Model):
    user = models.ForeignKey(
        to=get_user_model(), related_name='carer_profile', on_delete=models.CASCADE)
    facility_name = models.CharField(max_length=256)
    admin_name = models.CharField(max_length=256)
    image = models.ImageField(default='default_profile.png')
    phone = models.CharField(max_length=64)
    email = models.CharField(max_length=256)
    address = models.ForeignKey(to=Address, on_delete=models.CASCADE)
