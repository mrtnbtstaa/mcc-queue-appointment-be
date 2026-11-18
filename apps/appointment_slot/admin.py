from django.contrib import admin
from .models import AppointmentSlot

@admin.register(AppointmentSlot)
class AppointmentSlot(admin.ModelAdmin):
    pass