from rest_framework import serializers

from analysis.models import AnalysisSession


class AnalysisSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisSession
        fields = ('ecg_file', 'fs')

