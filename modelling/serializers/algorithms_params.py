from rest_framework import serializers


class KNNParamsSerializer(serializers.Serializer):
    n_neighbors = serializers.IntegerField(required=False, default=5)
    algorithm = serializers.ChoiceField(
        required=False,
        default="auto",
        choices=["auto", "ball_tree", "kd_tree", "brute"],
    )
    weights = serializers.ChoiceField(
        required=False, default="uniform", choices=["uniform", "distance"]
    )

    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class SVCParamsSerializer(serializers.Serializer):
    C = serializers.FloatField(required=False, default=1.0)
    kernel = serializers.ChoiceField(
        required=False, default="rbf", choices=["linear", "poly", "rbf", "sigmoid"]
    )
    degree = serializers.IntegerField(required=False, default=3)

    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class RandomForestParamsSerializer(serializers.Serializer):
    n_estimators = serializers.IntegerField(required=False, default=100)
    criterion = serializers.ChoiceField(
        required=False, default="gini", choices=["gini", "entropy"]
    )
    max_depth = serializers.IntegerField(required=False, allow_null=True, default=None)

    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass
