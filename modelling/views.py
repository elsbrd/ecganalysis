from copy import deepcopy

from django.db import transaction
from rest_framework.generics import RetrieveAPIView

from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from .constants.enums import ClassificationAlgorithm
from .models import TrainingSession
from .serializers import (
    KNNParamsSerializer,
    RandomForestParamsSerializer,
    SVCParamsSerializer,
    TrainingSessionGeneralParamsSerializer,
    TrainingSessionSerializer,
)
from .tasks import q_train_model


class TrainingSessionCreateView(APIView):
    ALGORITHM_SERIALIZER = {
        ClassificationAlgorithm.KNN: KNNParamsSerializer,
        ClassificationAlgorithm.SVC: SVCParamsSerializer,
        ClassificationAlgorithm.RANDOM_FOREST: RandomForestParamsSerializer,
    }

    def post(self, request):
        data = deepcopy(request.data)

        general_params = data.pop("general_params")
        general_params_serializer = TrainingSessionGeneralParamsSerializer(
            data=general_params
        )
        general_params_serializer.is_valid(raise_exception=True)
        general_params_validated = general_params_serializer.validated_data

        algorithm, algorithm_params = general_params_validated["algorithm"], data.pop(
            "algorithm_params"
        )
        algorithm_params_serializer = self.ALGORITHM_SERIALIZER[algorithm](
            data=algorithm_params
        )
        algorithm_params_serializer.is_valid(raise_exception=True)
        algorithm_params_validated = algorithm_params_serializer.validated_data

        training_session = TrainingSession.objects.create()
        training_session_id_str = str(training_session.id)

        transaction.on_commit(lambda: q_train_model.delay(
            training_session_id_str,
            general_params_validated,
            algorithm_params_validated,
        ))

        return Response({"id": training_session_id_str}, status=HTTP_201_CREATED)


class TrainingSessionRetrieveView(RetrieveAPIView):
    queryset = TrainingSession.objects.all()
    serializer_class = TrainingSessionSerializer
