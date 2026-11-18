from django.contrib import admin
from .models import DocumentService

@admin.register(DocumentService)
class DocumentService(admin.ModelAdmin):
    pass
