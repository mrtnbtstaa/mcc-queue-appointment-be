from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class Appointment(admin.ModelAdmin):
    pass
