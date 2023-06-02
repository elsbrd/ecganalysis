from django.urls import path

from . import views
from .apps import AnalysisConfig

app_name = AnalysisConfig.name

urlpatterns = [
    path("session/", views.AnalysisSessionView.as_view(), name="session-create"),
]
