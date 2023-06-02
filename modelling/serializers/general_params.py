from rest_framework import serializers

from modelling.constants.enums import ClassificationAlgorithm


class TrainingSessionGeneralParamsSerializer(serializers.Serializer):
    alphabet_size = serializers.IntegerField()
    word2vec_vector_size = serializers.IntegerField(required=False, default=100)
    algorithm = serializers.ChoiceField(
        choices=ClassificationAlgorithm.choices(),
        error_messages={"invalid_choice": "Invalid choice."},
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
