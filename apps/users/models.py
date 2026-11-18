import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models.timestamp_model import TimestampModel
from .manager import CustomUserManager
# Create your models here.

class UserRole(models.TextChoices):
    STUDENT = "student", "STUDENT"
    STAFF = "staff", "STAFF"

class Course(models.TextChoices):
    BSIT = "bsit", "BSIT"
    BSCS = "bscs", "BSCS"
    BSIS = "bsis", "BSIS"

class YearLevel(models.TextChoices):
    FIRST_YEAR = "1", "First Year"
    SECOND_YEAR = "2", "Second Year"
    THIRD_YEAR = "3", "Third Year"
    FOURTH_YEAR = "4", "Fourth Year"

class User(AbstractUser, TimestampModel):

    username = None 
    first_name = None
    last_name = None

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(unique=True)
    student_id = models.CharField(unique=True, null=True,  blank=True)

    course = models.CharField(
        choices=Course.choices,
        max_length=10,
        null=True,
        blank=True
    )
    year_level = models.CharField(
        choices=YearLevel.choices,
        max_length=15,
        null=True,       
        blank=True
    )

    name = models.CharField(max_length=100, null=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        choices=UserRole.choices,
        max_length=20,
        default=UserRole.STUDENT
    )
    is_deleted = models.BooleanField(default=False)

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                name="unique_user_email"
            ),
            models.UniqueConstraint(
                fields=["student_id"],
                name="unique_user_student_id"
            ),
        ]


    