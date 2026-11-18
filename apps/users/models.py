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
    BSHM = "bshm", "BSHM"
    BSTM = "bstm", "BSTM"
    BSA = "bsa", "BSA"
    BSCA = "bsca", "BSCA"
    BSE = "bse", "BSE"
    BSMA = "bsma", "BSMA"
    BSOA = "bsoa", "BSOA"
    BEED = "beed", "BEED"
    BECED = "beced", "BECED"
    BSED_ENGLISH = "bsed-english", "BSED English"
    BSED_FILIPINO = "bsed-filipino", "BSED Filipino"
    BSED_MATH = "bsed-math", "BSED Math"
    BSED_SCIENCE = "bsed-science", "BSED Science"
    BSED_SOCIAL_STUDIES = "bsed-social-studies", "BSED Social Studies"
    BPED = "bped", "BPED"
    BTVTE = "btvte", "BTVTE"
    AB_HISTORY = "ab-history", "AB History"
    AB_PSYCHOLOGY = "ab-psychology", "AB Psychology"
    BPA = "bpa", "BPA"
    BSBIO = "bsbio", "BSBIO"
    BSLM = "bslm", "BSLM"

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
        max_length=30,
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


    