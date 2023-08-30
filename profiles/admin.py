from django.contrib import admin

from profiles.models import CarerProfile, StudentProfile

admin.site.register(StudentProfile)
admin.site.register(CarerProfile)
