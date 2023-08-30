from django.contrib import admin

from rentals.models import Rental, RentalContract

admin.site.register(Rental)
admin.site.register(RentalContract)
