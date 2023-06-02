import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


def get_ecg_file_upload_to(_, filename):
    date = timezone.now().date()
    return f"media/ecg/{date}/{filename}"


class AnalysisSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ecg_file = models.FileField(
        upload_to=get_ecg_file_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["csv", "xlsx"])],
    )
    fs = models.IntegerField(default=360)

    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
