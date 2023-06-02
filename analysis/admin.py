from django.contrib import admin

from analysis.models import AnalysisSession


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )
    ordering = ("-created_at",)
