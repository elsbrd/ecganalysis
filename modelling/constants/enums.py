from common.constants.enums import ChoicesEnum


class ClassificationAlgorithm(str, ChoicesEnum):
    KNN = "knn"
    SVC = "svc"
    RANDOM_FOREST = "random_forest"


class TrainingSessionStatus(str, ChoicesEnum):
    INITIALIZED = "initialized"
    TRAINING = "training"
    EVALUATION = "evaluation"
    DONE = "done"
