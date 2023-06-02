from django.contrib import admin

from modelling.models import TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "classifier_name",
        "test_accuracy",
        "created_at",
    )
    ordering = ("-created_at",)
