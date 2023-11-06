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

# ECG Analysis Service Web Application

This section of the README provides visual insights into the ECG Analysis Service application’s interface and functionality.

## Home Page

Upon launching the ECG Analysis Service, users are greeted with a homepage that features input fields and buttons to navigate the service.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/dc4cb50e-a2f7-4ed3-8860-85eafcec3645)

*Main software page*

Clicking the button reveals the modeling section.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/17fa1608-04f6-4bdb-98b8-a60344d09270)

*Modeling section*

## Modeling

Entering training parameters is straightforward and intuitive.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/3a2492a0-5762-4165-b97a-be109fd03e5a)

*Entering training parameters*

Should mandatory parameters be omitted, the system prompts an error message.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/6faf3fd2-0d00-4f80-bc3e-37a6c09ba2fc)

*Error for unfilled fields*

Similarly, an error is displayed if the data type of the input is incorrect.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/7a0d6f91-29c0-45c6-a908-c0a6d89f0e9a)

*Error for the wrong data type*

The modeling process progresses through various statuses which are displayed to the user.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/7e550b00-5d54-4a89-8fad-6c74f0329e27)

*Status initialized*

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/fe78ac38-bcbd-4065-a328-af98566e5de3)

*Status training*

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/38993186-cc8c-46b0-8025-b995b1cde8b4)

*Status evaluating*

Upon successful training, the model metrics and graphs are displayed.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/74f569c2-55df-41c0-9386-931c75073819)

*Display of model metrics and graphs*

## Analysis

The analysis begins with the uploading of an ECG file.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/2100361f-b5b8-4db1-a83e-bb6f296b051a)

*Upload ECG file*

If the selected file is not in the CSV or XLSX format, the system informs the user of the error.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/8d676675-f95a-4d6e-8cd6-05572ba7a2f2)

*Error for incorrect file format*

If the uploaded file exceeds the permissible limit of 5MB, an error is displayed.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/cd037f0d-182a-4597-8106-5796a58471b2)

*Uploaded file size exceeds the permissible limit*

Analysis of the ECG file results in the display of a chart with marked cardiac components and predicted labels.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/64692dc5-60de-416a-aaac-093d7f3d0172)

*Successful ECG file analysis*

This is accompanied by a table detailing the heartbeats, predicted labels, word representations of the beats, and their vector forms.

![image](https://github.com/elsbrd/ecganalysis/assets/56909624/43c7c738-0aea-44a3-afa2-60061dec5271)

*Table with heartbeats*
