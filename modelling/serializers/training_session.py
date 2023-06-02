from rest_framework import serializers

from modelling.models import TrainingSession


class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = (
            "status",
            "train_accuracy",
            "test_accuracy",
            "precision",
            "recall",
            "f1_score",
            "silhouette_score",
            "charts",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field in [
            "train_accuracy",
            "test_accuracy",
            "precision",
            "recall",
            "f1_score",
            "silhouette_score",
        ]:
            if representation[field] is not None:
                representation[field] = "{:.1f}%".format(representation[field] * 100)
        return representation
