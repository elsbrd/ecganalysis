import os

from django.conf import settings

from modelling.apps import ModellingConfig

MITDB = "mitdb"
SCALER = "scaler"
KMEANS = "kmeans"
WORD2VEC = "word2vec"
CLASSIFIER = "classifier"

MODELLING_APP_DIR = os.path.join(settings.BASE_DIR, ModellingConfig.name)

MODELS_CACHE_DIR = os.path.join(MODELLING_APP_DIR, "models_cache")
SCALER_MODELS_CACHE_DIR = os.path.join(MODELS_CACHE_DIR, SCALER)
KMEANS_MODELS_CACHE_DIR = os.path.join(MODELS_CACHE_DIR, KMEANS)
WORD2VEC_MODELS_CACHE_DIR = os.path.join(MODELS_CACHE_DIR, WORD2VEC)
CLASSIFIER_MODELS_CACHE_DIR = os.path.join(MODELS_CACHE_DIR, CLASSIFIER)

DATA_PREPARATION_CACHE_DIR = os.path.join(
    MODELLING_APP_DIR, "data_preparation", "cache"
)
MITDB_DATASET_DIR = os.path.join(DATA_PREPARATION_CACHE_DIR, "datasets", MITDB)
MITDB_FEATURES_DIR = os.path.join(DATA_PREPARATION_CACHE_DIR, "features", MITDB)
