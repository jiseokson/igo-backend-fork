from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models

from profiles.models import Address

ACTIVITY_CATEGORY_CHOICES = (
    ('스마트폰 사용법', '스마트폰 사용법'),
    ('SNS 활용법', 'SNS 활용법'),
    ('유튜브 활용법', '유튜브 활용법'),
    ('키오스크 활용', '키오스크 활용'),
)


class Program(models.Model):
    title = models.CharField(max_length=256)
    author = models.ForeignKey(
        to=get_user_model(), related_name='author', on_delete=models.CASCADE)
    content = models.TextField()
    reward = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    regist_start_at = models.DateField()
    regist_end_at = models.DateField()

    activity_start_at = models.DateField()
    activity_end_at = models.DateField()

    subscriber_limit = models.IntegerField()
    subscriber = models.ManyToManyField(
        to=get_user_model(), related_name='program')

    activity_category = models.CharField(
        max_length=100, choices=ACTIVITY_CATEGORY_CHOICES, blank=True)
    address = models.ForeignKey(to=Address, on_delete=models.CASCADE)

    is_rewarded = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_registing(self):
        return self.regist_start_at <= timezone.now().date() <= self.regist_end_at and self.subscriber.count() < self.subscriber_limit

    @property
    def activity_status(self):
        if timezone.now().date() < self.activity_start_at:
            return 'before'
        elif self.activity_start_at <= timezone.now().date() <= self.activity_end_at:
            return 'now'
        else:
            return 'done'

    @property
    def regist_status(self):
        if timezone.now().date() < self.regist_start_at:
            return 'before'
        elif self.is_registing:
            return 'now'
        else:
            return 'done'
