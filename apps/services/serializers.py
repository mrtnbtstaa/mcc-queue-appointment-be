from rest_framework import serializers

from common.serializers.fields import RequiredCharField, RequiredListField
from .models import DocumentService, ServiceCategory


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

    name = RequiredCharField(label="Service Name", max_length=255)

    category = RequiredCharField(
        label="Category",
        write_only=True
    )
    
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

        category = attrs.get("category")

        if category not in ServiceCategory.values:
            raise serializers.ValidationError({
                "category": ["Invalid category value."]
            })

        query = DocumentService.objects.filter(category=category)

        if self.instance:
            query = query.exclude(pk=self.instance.pk)

        if query.exists():
            raise serializers.ValidationError({
                "category": ["A service with this category already exists."]
            })


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