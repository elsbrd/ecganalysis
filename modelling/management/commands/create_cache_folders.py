import os

from django.core.management import BaseCommand

from modelling.constants import DATA_PREPARATION_CACHE_DIR, MITDB_DATASET_DIR, MITDB_FEATURES_DIR, MODELS_CACHE_DIR, \
    SCALER_MODELS_CACHE_DIR, KMEANS_MODELS_CACHE_DIR, WORD2VEC_MODELS_CACHE_DIR, CLASSIFIER_MODELS_CACHE_DIR


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
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

