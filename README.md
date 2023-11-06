# ECG Modeling and Analysis System

This project is developed to provide users with the ability to model and analyze electrocardiograms (ECGs) using modern machine learning algorithms.

## Description
This system allows for intricate modeling and analysis of ECG data, with user-driven parameters to influence machine learning training, algorithm selection, and evaluation. It serves as a comprehensive tool for understanding and interpreting cardiac signals.

## Key Components

### Modeling

- **User Interface**: Allows users to input training parameters, choose algorithms, and configure their parameters.
- **Algorithms**: Includes KMeans, Word2Vec, various heartbeat classification algorithms such as random forest, and SVC.
- **Model Evaluation**: Outputs precision, recall, F1-score metrics, and the silhouette score for KMeans.
- **Visualization**: Presents t-SNE plots for clustered P, QRS, T waves, and confusion matrices.

### Analysis

- **Data Upload**: Capability to upload personal ECG data in csv/xlsx formats.
- **Heartbeat Classification**: Processes ECG records with annotations of normal and abnormal heartbeats.
- **Results Visualization**: Graph with heartbeat class markings and a detailed information table.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them:

- Python 3.8 or higher
- pip (Python package manager)
- Virtualenv (optional but recommended for creating isolated Python environments)

### Installing

A step-by-step series of examples that tell you how to get a development environment running:

Clone the repository:
```
git clone https://github.com/elsbrd/ecganalysis.git
cd ecganalysis
```

Create a virtual environment and activate it (optional):
```
virtualenv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the required packages:
```
pip install -r requirements.txt
```

Migrate the database:
```
python manage.py migrate
```

Run the development server:
```
python manage.py runserver
```

The API should now be accessible at `http://127.0.0.1:8000/`.
