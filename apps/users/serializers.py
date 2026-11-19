from rest_framework import serializers
from common.serializers.fields import RequiredCharField, RequiredEmailField, RequiredBoolField
from .models import User, Course

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
        read_only_fields = (
            "role",
            "id"
        )

    def validate(self, attrs):

        if attrs["course"] not in Course.values:
            raise serializers.ValidationError({
                "course": ["Invalid course value."]
            })

        return attrs

    def update(self, instance, validated_data):

        email = validated_data.get("email")

        # Only update the email if the value is not the same to the current email
        if email and email != instance.email:
            instance.email = email

        instance.course = validated_data.get("course", instance.course)
        instance.year_level = validated_data.get("year_level", instance.year_level)
        instance.is_active = validated_data.get("is_active", instance.is_active)

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