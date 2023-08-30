from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

from profiles.models import Address


CATEGORY_CHOICES = [
    ('스마트폰', '스마트폰'),
    ('태블릿', '태블릿'),
    ('노트북', '노트북'),
]


class Rental(models.Model):
    manufacturer = models.CharField(max_length=256)
    # iPhone 14, Galaxy 22 처럼 일반 사람들이 아는 그 이름
    model_name = models.CharField(max_length=256)
    # SM-f711N 처럼 제조 등록 코드
    model_code = models.CharField(max_length=256)
    category = models.CharField(
        max_length=128, choices=CATEGORY_CHOICES)
    image = models.ImageField()
    manufacturing_date = models.DateField()
    registration_date = models.DateField(auto_now_add=True)
    battery_capacity = models.IntegerField()
    memory_amount = models.IntegerField()
    is_active = models.BooleanField(default=True)
    rental_start_at = models.DateField()
    rental_end_at = models.DateField()
    point = models.IntegerField()


class RentalContract(models.Model):
    borrower = models.ForeignKey(
        to=get_user_model(), related_name="rental_contract", on_delete=models.CASCADE)
    rental = models.ForeignKey(
        to=Rental, related_name='rental_contract', on_delete=models.CASCADE)

    subscribe_date = models.DateField(auto_now_add=True)
    rental_start_at = models.DateField()
    rental_end_at = models.DateField()

    addressee_name = models.CharField(max_length=256)
    addressee_phone = models.CharField(max_length=64)
    # address = models.CharField(max_length=256)
    address = models.ForeignKey(
        to=Address, related_name='rental_contract', on_delete=models.CASCADE)

    @property
    def status(self):
        if timezone.now().date() < self.rental_start_at:
            return 'before'
        elif self.rental_start_at <= timezone.now().date() <= self.rental_end_at:
            return 'now'
        else:
            return 'done'
