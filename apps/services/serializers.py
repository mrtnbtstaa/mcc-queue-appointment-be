from rest_framework import serializers

from common.serializers.fields import RequiredCharField, RequiredListField
from .models import DocumentService


# ------------------------------------------
# DocumentService serializers
# ------------------------------------------
class DocumentServiceListSerializer(serializers.ModelSerializer):
    """Lean payload for list/retrieve."""

    category_display = serializers.CharField(source="get_category_display", read_only=True)
    fee_display = serializers.CharField(read_only=True)
    processing_duration = serializers.CharField(source="processing_duration_display", read_only=True)
    
    required_documents = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )

    class Meta:
        model = DocumentService
        fields = (
            "id",
            "name",
            "category",
            "category_display",
            "fee",
            "fee_display",
            "duration_min",
            "duration_max",
            "processing_duration",
            "required_documents",
            "is_active",
        )


class DocumentServiceWriteSerializer(serializers.ModelSerializer):
    """Used for create/update."""

    # 1. Using RequiredCharField for the Name
    name = RequiredCharField(label="Service Name", max_length=255)
    
    # 2. Using RequiredListField for Required Documents
    # Note: RequiredListField requires a min_length. I set it to 1.
    # If you allow services with NO required documents, change to min_length=0 
    # (but RequiredListField forces allow_empty=False by default).
    required_documents = RequiredListField(
        label="Required Student Documents",
        min_length=1,
        child=RequiredCharField(label="Document Name", max_length=255),
        required=False,
    )

    class Meta:
        model = DocumentService
        fields = (
            "name",
            "category",
            "fee",
            "duration_min",
            "duration_max",
            "required_documents",
            "is_active",
        )

    def validate(self, attrs):
        duration_min = attrs.get("duration_min", getattr(self.instance, "duration_min", 0))
        duration_max = attrs.get("duration_max", getattr(self.instance, "duration_max", 0))
        if duration_max < duration_min:
            raise serializers.ValidationError(
                {"duration_max": ["Maximum duration cannot be less than the minimum duration."]}
            )
        return attrs


# ------------------------------------------
# Activation / Deactivation serializer
# ------------------------------------------
class DocumentServiceStatusSerializer(serializers.ModelSerializer):
    
    is_active = serializers.BooleanField(
        required=True, 
        label="Active Status"
    )

    class Meta:
        model = DocumentService
        fields = ("is_active",)