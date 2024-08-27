import argparse
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve, precision_recall_curve, average_precision_score

parser = argparse.ArgumentParser()
parser.add_argument("--data-path", type = str, help = "Data location")
args = parser.parse_args()
# Read data
print("\nReading data")
df_train = pd.read_csv(args.data_path)
print("\nData is done")

# Data for training and validation
print("\nStarting defining the data for training and validation")
target_variable = "income"
df_train = pd.read_csv(args.data_path)
x = df_train.drop(target_variable, axis = 1)
y = df_train[target_variable]

x_train, x_val, y_train, y_val = train_test_split(x, y, test_size = 0.2, random_state = 42)

print("x_train shape:", x_train.shape)
print("x_val shape:", x_val.shape)
print("y_train shape:", y_train.shape)
print("y_val shape:", y_val.shape)
print("\nData for training and testing are done")

# Data transformation
print("\nStarting applying target variable transformation")
y_train = y_train.map(lambda x: 0 if x == "<=50K" else 1)
y_val = y_val.map(lambda x: 0 if x == "<=50K" else 1)
print("\nTarget variable transformation is done")

print("\nStarting defining data transformation steps for categorical features")
categorical_features = ["workclass", "education", "marital-status", "occupation", "relationship", "race", "sex", "native-country"]
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", OneHotEncoder(sparse_output = False, drop = "first"), categorical_features)
    ])
print("\nData transformation for categorical features is done")

# Classifiers
print("\nStarting defining the classifiers")
logistic = LogisticRegression(class_weight = "balanced")
random_forest = RandomForestClassifier()
mlp = MLPClassifier()
print("\nClassifiers are done")

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", logistic)
])

# Hyperparameters per classifier
print("\nStarting defining the hyperparameters")
param_grid = [
    {
        "classifier": [logistic],

        # Regularization strength, smaller values specify stronger regularization
        "classifier__C": [0.01, 0.1, 1, 10, 100],

        # Optimizer algorithm
        "classifier__solver": ["liblinear", "sag", "saga"],

        "classifier__penalty": ["l2"]
    }
]
print("\nHyperparameters are done")

# Training
print("\nStarting training")
random_search = RandomizedSearchCV(pipeline, param_grid, n_iter = 100, cv=3, verbose = 2, random_state = 42, n_jobs = -1)
random_search.fit(x_train, y_train)

print("Best hyperparameters:", random_search.best_params_)
print("Best score: ", random_search.best_score_)

print("\nTraining is done")

# Prediction
print("\nStarting evaluation")
y_pred = random_search.predict(x_val)

# Probabilities for ROC AUC
y_prob = random_search.predict_proba(x_val)[:, 1]

# Classification Report
print("\nClassification Report:", classification_report(y_val, y_pred))

# Confusion Matrix
print("\nConfusion Matrix:", confusion_matrix(y_val, y_pred))

# ROC AUC Score
roc_auc = roc_auc_score(y_val, y_prob)
print("\nROC AUC Score:", roc_auc)

# Precision-Recall AUC Score
average_precision = average_precision_score(y_val, y_prob)
print("\nPrecision-Recall AUC Score:", average_precision)

print("\Evaluation is done")
