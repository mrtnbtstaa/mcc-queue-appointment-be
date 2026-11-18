from django.contrib import admin
from .models import Queue


@admin.register(Queue)
class Queue(admin.ModelAdmin):
    pass