import os

from django.core.management import BaseCommand

from modelling.constants import (
    CLASSIFIER_MODELS_CACHE_DIR,
    DATA_PREPARATION_CACHE_DIR,
    KMEANS_MODELS_CACHE_DIR,
    MITDB_DATASET_DIR,
    MITDB_FEATURES_DIR,
    MODELS_CACHE_DIR,
    SCALER_MODELS_CACHE_DIR,
    WORD2VEC_MODELS_CACHE_DIR,
)
from modelling.data_preparation.manager import MITDBDatasetManager


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        manager = MITDBDatasetManager()
        manager.cache_features()
