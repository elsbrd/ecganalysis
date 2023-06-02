from django.urls import path

from . import views

app_name = "modelling"

urlpatterns = [
    path(
        "session/",
        views.TrainingSessionCreateView.as_view(),
        name="training-session-create",
    ),
    path(
        "session/<uuid:pk>/",
        views.TrainingSessionRetrieveView.as_view(),
        name="training-session-retrieve",
    ),
]
