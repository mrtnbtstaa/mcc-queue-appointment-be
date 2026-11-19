from rest_framework import serializers
from common.serializers.fields import RequiredCharField, RequiredEmailField, RequiredBoolField
from .models import User, Course, YearLevel

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = (
            "last_login",
            "is_superuser",
            "password",
            "is_staff",
            "groups",
            "user_permissions",
            "email_verified",
            "updated_at",
            "created_at",
            "is_deleted",
            "deleted_at",
            "date_joined"
        )

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = (
            "last_login",
            "is_superuser",
            "password",
            "is_staff",
            "groups",
            "user_permissions",
            "email_verified",
            "updated_at",
            "created_at",
            "is_deleted",
            "deleted_at",
            "date_joined"
        )

class UserUpdateProfileSerializer(serializers.ModelSerializer):

    name = RequiredCharField(
        write_only=True,
        label="Full Name"
    )

    student_id = RequiredCharField(
        write_only=True,
        label="Student ID"
    )

    email = RequiredEmailField(
        write_only=True,
        label="Email"
    )

    course = RequiredCharField(
        write_only=True,
        label="Course"
    )
    year_level = RequiredCharField(
        write_only=True,
        label="Year Level"
    )
    is_active = RequiredBoolField(
        write_only=True,
        label="Is Active"
    )

    class Meta:
        model = User
        fields = (
            "name",
            "student_id",
            "email",
            "course",
            "year_level",
            "is_active"
        )

    def validate(self, attrs):

        # PATCH requests only contain the fields that changed, so every lookup
        # must tolerate the field being absent.
        course = attrs.get("course")
        if course is not None and course not in Course.values:
            raise serializers.ValidationError({
                "course": ["Invalid course value."]
            })

        year_level = attrs.get("year_level")
        if year_level is not None and year_level not in YearLevel.values:
            raise serializers.ValidationError({
                "year_level": ["Invalid year level value."]
            })

        if self.instance is not None:
            email = attrs.get("email")
            if (
                email
                and email.lower() != (self.instance.email or "").lower()
                and User.objects.filter(email__iexact=email)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise serializers.ValidationError({
                    "email": ["Email is already registered."]
                })

            student_id = attrs.get("student_id")
            if (
                student_id
                and student_id != self.instance.student_id
                and User.objects.filter(student_id=student_id)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise serializers.ValidationError({
                    "student_id": ["Student ID is already in use."]
                })

        return attrs

    def update(self, instance, validated_data):

        for field in (
            "name",
            "student_id",
            "email",
            "course",
            "year_level",
            "is_active",
        ):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()

        return instance
# ------------------------------------------
# Resend verification serializer
# ------------------------------------------
class ResendVerificationSerializer(serializers.ModelSerializer):

    email = RequiredEmailField(write_only=True, label="Email")

    class Meta:
        model = User
        fields = ("email")