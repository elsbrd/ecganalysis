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
        self.__create_dirs()

        manager = MITDBDatasetManager()
        manager.cache_features()

    def __create_dirs(self):
        if not os.path.isdir(DATA_PREPARATION_CACHE_DIR):
            os.mkdir(DATA_PREPARATION_CACHE_DIR)

        if not os.path.isdir(MITDB_DATASET_DIR):
            os.makedirs(MITDB_DATASET_DIR)

        if not os.path.isdir(MITDB_FEATURES_DIR):
            os.makedirs(MITDB_FEATURES_DIR)

        if not os.path.isdir(MODELS_CACHE_DIR):
            os.mkdir(MODELS_CACHE_DIR)

        if not os.path.isdir(SCALER_MODELS_CACHE_DIR):
            os.mkdir(SCALER_MODELS_CACHE_DIR)

        if not os.path.isdir(KMEANS_MODELS_CACHE_DIR):
            os.mkdir(KMEANS_MODELS_CACHE_DIR)

        if not os.path.isdir(WORD2VEC_MODELS_CACHE_DIR):
            os.mkdir(WORD2VEC_MODELS_CACHE_DIR)

        if not os.path.isdir(CLASSIFIER_MODELS_CACHE_DIR):
            os.mkdir(CLASSIFIER_MODELS_CACHE_DIR)
