import io
import json
from typing import Union

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from django.core.files.base import ContentFile
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.manifold import TSNE
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from modelling.constants.enums import ClassificationAlgorithm, TrainingSessionStatus
from modelling.data_preparation.manager import MITDBDatasetManager
from modelling.data_preparation.utils import (
    concatenate_letters,
    convert_labels_to_letters,
    word_to_vec,
)

ALGORITHM_CLASS = {
    ClassificationAlgorithm.KNN: KNeighborsClassifier,
    ClassificationAlgorithm.SVC: SVC,
    ClassificationAlgorithm.RANDOM_FOREST: RandomForestClassifier,
}


class TrainingManager:
    kmeans_p: KMeans
    kmeans_qrs: KMeans
    kmeans_t: KMeans
    word2vec: Word2Vec
    classifier: Union[KNeighborsClassifier, SVC, RandomForestClassifier]

    X_train: list
    X_test: list
    y_train: list
    y_test: list

    p_wave_features: np.ndarray
    qrs_complex_features: np.ndarray
    t_wave_features: np.ndarray

    labels_p: np.ndarray
    labels_qrs: np.ndarray
    labels_t: np.ndarray

    letters_p: np.ndarray
    letters_qrs: np.ndarray
    letters_t: np.ndarray

    def __init__(self, training_session, general_params, algorithm_params):
        self._session = training_session

        self.__general_params = general_params
        self.__algorithm_params = algorithm_params

    def run(self):
        self._session.status = TrainingSessionStatus.TRAINING
        self._session.classifier_name = self.__general_params["algorithm"]
        self._session.save()

        self._train()

        self._session.status = TrainingSessionStatus.EVALUATION
        self._session.save()

        self._evaluate()

        self._save()

        self._session.status = TrainingSessionStatus.DONE
        self._session.save()

    def _train(self):
        dataset_manager = MITDBDatasetManager()

        (
            self.p_wave_features,
            self.qrs_complex_features,
            self.t_wave_features,
            heartbeat_annotations,
        ) = dataset_manager.load_features_and_annotations_from_cache()

        words = self._generate_words()

        vectors = self._generate_vectors(words)

        self._fit_classifier(vectors, heartbeat_annotations)

    def _evaluate(self):
        # Predictions on training data
        y_train_pred = self.classifier.predict(self.X_train)

        # Predictions on testing data
        y_test_pred = self.classifier.predict(self.X_test)

        # Calculate metrics for training data
        train_accuracy = accuracy_score(self.y_train, y_train_pred)

        # Calculate metrics for testing data
        test_accuracy = accuracy_score(self.y_test, y_test_pred)
        precision = precision_score(self.y_test, y_test_pred, average="weighted")
        recall = recall_score(self.y_test, y_test_pred, average="weighted")
        f1 = f1_score(self.y_test, y_test_pred, average="weighted")

        silhouette_p = silhouette_score(self.p_wave_features, self.labels_p)
        silhouette_qrs = silhouette_score(self.qrs_complex_features, self.labels_qrs)
        silhouette_t = silhouette_score(self.t_wave_features, self.labels_t)
        silhouette_avg = (silhouette_p + silhouette_qrs + silhouette_t) / 3

        charts = {
            "tsne": self._get_tsne_plots(),
            "confusion_matrix": self._get_confusion_matrix_plot(y_test_pred),
        }

        self._session.train_accuracy = train_accuracy
        self._session.test_accuracy = test_accuracy
        self._session.precision = precision
        self._session.recall = recall
        self._session.f1_score = f1
        self._session.silhouette_score = silhouette_avg
        self._session.charts = json.dumps(charts)

    def _save(self):
        self.__save_model_to_field(
            self.kmeans_p, self._session.kmeans_p_model, f"p_{self._session.id}"
        )
        self.__save_model_to_field(
            self.kmeans_qrs, self._session.kmeans_qrs_model, f"qrs_{self._session.id}"
        )
        self.__save_model_to_field(
            self.kmeans_t, self._session.kmeans_t_model, f"t_{self._session.id}"
        )
        self.__save_model_to_field(
            self.word2vec, self._session.word2vec_model, f"{self._session.id}"
        )
        self.__save_model_to_field(
            self.classifier, self._session.classifier_model, f"{self._session.id}"
        )

    def _generate_words(self):
        n_clusters = self.__general_params["alphabet_size"]

        self.kmeans_p = KMeans(n_clusters=n_clusters)
        self.kmeans_qrs = KMeans(n_clusters=n_clusters)
        self.kmeans_t = KMeans(n_clusters=n_clusters)

        self.labels_p = self.kmeans_p.fit_predict(self.p_wave_features)
        self.labels_qrs = self.kmeans_qrs.fit_predict(self.qrs_complex_features)
        self.labels_t = self.kmeans_t.fit_predict(self.t_wave_features)

        self.letters_p = convert_labels_to_letters(self.labels_p)
        self.letters_qrs = convert_labels_to_letters(self.labels_qrs)
        self.letters_t = convert_labels_to_letters(self.labels_t)

        words = concatenate_letters(self.letters_p, self.letters_qrs, self.letters_t)

        return words

    def _generate_vectors(self, words):
        sentences = [list(word) for word in words]

        self.word2vec = Word2Vec(sentences, vector_size=50, window=3, min_count=1)
        vectors = [word_to_vec(word, self.word2vec) for word in words]

        return vectors

    def _fit_classifier(self, vectors, heartbeat_annotations):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            vectors, heartbeat_annotations, test_size=0.2, random_state=42
        )

        classifier_cls = ALGORITHM_CLASS[self.__general_params["algorithm"]]
        classifier = classifier_cls(**self.__algorithm_params)
        classifier.fit(self.X_train, self.y_train)

        self.classifier = classifier

    def _get_tsne_plots(
        self,
    ):
        sample_size = 500

        p_wave_features_sample, letters_p_sample = self.__sample_features(
            self.p_wave_features, self.letters_p, sample_size
        )
        qrs_complex_features_sample, letters_qrs_sample = self.__sample_features(
            self.qrs_complex_features, self.letters_qrs, sample_size
        )
        t_wave_features_sample, letters_t_sample = self.__sample_features(
            self.t_wave_features, self.letters_t, sample_size
        )

        # Plot t-SNE for each wave sample
        p_tsne_fig = self.__tsne_plot(p_wave_features_sample, letters_p_sample)
        qrs_tsne_fig = self.__tsne_plot(qrs_complex_features_sample, letters_qrs_sample)
        t_tsne_fig = self.__tsne_plot(t_wave_features_sample, letters_t_sample)

        return {
            "p": p_tsne_fig.to_json(),
            "qrs": qrs_tsne_fig.to_json(),
            "t": t_tsne_fig.to_json(),
        }

    def _get_confusion_matrix_plot(self, y_pred):
        # Compute confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)

        # Turn it into a DataFrame
        cm_df = pd.DataFrame(
            cm, index=self.classifier.classes_, columns=self.classifier.classes_
        )

        # Create the Plotly Figure
        fig = ff.create_annotated_heatmap(
            z=cm_df.values,
            x=list(cm_df.columns),
            y=list(cm_df.index),
            colorscale="Blues",
        )

        fig.update_layout(
            xaxis=dict(title="Predicted label"),
            yaxis=dict(title="True label"),
            autosize=True,
            margin=dict(l=0, r=0, b=0, t=0, pad=0),
        )

        return fig.to_json()

    @staticmethod
    def __tsne_plot(features, labels):
        tsne = TSNE(n_components=2)
        features_2d = tsne.fit_transform(features)

        # Create dataframe for Plotly
        df = pd.DataFrame(
            data={
                "x": features_2d[:, 0],
                "y": features_2d[:, 1],
                "Cluster": labels,
            }
        )

        # Create a plotly express scatter plot
        fig = px.scatter(df, x="x", y="y", color="Cluster")

        # Remove axis labels
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        # Remove chart borders
        fig.update_xaxes(showline=False, zeroline=False)
        fig.update_yaxes(showline=False, zeroline=False)

        # Remove title and axis titles
        fig.update_layout(
            showlegend=True,
            autosize=True,
            title=None,
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=0, r=0, t=0, b=0),  # This line reduces the chart borders
        )

        return fig

    @staticmethod
    def __save_model_to_field(model, field, name):
        # Dump the model into a bytes buffer
        buffer = io.BytesIO()
        joblib.dump(model, buffer)
        buffer.seek(0)

        # Save the buffer content to the field
        field.save(f"{name}.pkl", ContentFile(buffer.read()))

    @staticmethod
    def __sample_features(features, labels, size):
        features = np.array(features)
        labels = np.array(labels)
        if len(features) > size:
            indices = np.random.choice(len(features), size=size, replace=False)
            return features[indices], labels[indices]
        return features, labels
