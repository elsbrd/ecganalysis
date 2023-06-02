from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from modelling.models import TrainingSession

from .models import AnalysisSession
from .serializers.analysis_session import AnalysisSessionSerializer
from .utils.analyzer import ECGAnalyzer


class AnalysisSessionView(GenericAPIView):
    serializer_class = AnalysisSessionSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        analysis_session = serializer.save()

        training_session = self._get_training_session()

        analyzer = ECGAnalyzer(analysis_session, training_session)
        data = analyzer.get_analysis_result()

        return Response(data)

    def _get_training_session(self):
        training_session_id = self.request.data.get("training_session_id")
        training_session = TrainingSession.objects.filter(
            pk=training_session_id
        ).first()
        if not training_session:
            raise NotFound(
                {"detail": ["Training session with this ID could not be found."]}
            )

        return training_session
