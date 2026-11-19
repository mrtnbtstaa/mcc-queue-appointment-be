from django.db import models
from django.core.validators import MinValueValidator
import uuid

class ServiceCategory(models.TextChoices):
    ACADEMIC_ENROLLMENT = "Enrollment", "Academic Enrollment"
    FINANCIAL_CLEARANCE = "Certificates", "Certificates"
    GRADUATION = "Records", "Transcript & Records"

class DocumentService(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        max_length=255, 
        help_text="e.g., Certificate of Enrollment"
    )
    
    category = models.CharField(
        max_length=50,
        choices=ServiceCategory.choices,
        default=ServiceCategory.ACADEMIC_ENROLLMENT,
    )
    
    fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)],
        help_text="Fee in PHP (₱)"
    )
    
    duration_min = models.PositiveIntegerField(default=15)
    duration_max = models.PositiveIntegerField(default=30)
    
    # --- THE CHANGE ---
    # Using ArrayField (PostgreSQL only). 
    # Use JSONField(default=list) if using SQLite/MySQL.
    required_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of required documents (e.g., ['Student ID', 'Request Slip'])"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name