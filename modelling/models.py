import uuid

import joblib
from django.core.files.storage import FileSystemStorage
from django.db import models

from modelling.constants import CLASSIFIER, KMEANS, MODELS_CACHE_DIR, WORD2VEC
from modelling.constants.enums import TrainingSessionStatus

MODELS_STORAGE = FileSystemStorage(location=MODELS_CACHE_DIR)


class TrainingSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    status = models.CharField(
        max_length=20,
        choices=TrainingSessionStatus.choices(),
        default=TrainingSessionStatus.INITIALIZED,
    )

    # Models
    kmeans_p_model = models.FileField(
        storage=MODELS_STORAGE, upload_to=f"{KMEANS}/", null=True
    )
    kmeans_qrs_model = models.FileField(
        storage=MODELS_STORAGE, upload_to=f"{KMEANS}/", null=True
    )
    kmeans_t_model = models.FileField(
        storage=MODELS_STORAGE, upload_to=f"{KMEANS}/", null=True
    )
    word2vec_model = models.FileField(
        storage=MODELS_STORAGE, upload_to=f"{WORD2VEC}/", null=True
    )
    classifier_model = models.FileField(
        storage=MODELS_STORAGE, upload_to=f"{CLASSIFIER}/", null=True
    )
    classifier_name = models.CharField(max_length=100, blank=True)

    # Metrics
    train_accuracy = models.FloatField(null=True)
    test_accuracy = models.FloatField(null=True)
    precision = models.FloatField(null=True)
    recall = models.FloatField(null=True)
    f1_score = models.FloatField(null=True)
    silhouette_score = models.FloatField(null=True)

    # Charts
    charts = models.JSONField(default=dict)

    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TrainingSession({self.classifier_name})"

    def get_kmeans_models(self):
        return (
            joblib.load(self.kmeans_p_model),
            joblib.load(self.kmeans_qrs_model),
            joblib.load(self.kmeans_t_model),
        )

    def get_word2vec_model(self):
        return joblib.load(self.word2vec_model)

    def get_classifier_model(self):
        return joblib.load(self.classifier_model)
