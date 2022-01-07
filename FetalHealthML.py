# -*- coding: utf-8 -*-
"""FetalHealth.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Au6JpBeGQjgBKgoOVTPscjKFy6To8fiz

### **Fetal Health Classification**

# Import libraries to be used
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV, StratifiedKFold

"""# Exploratory Data Analysis and Pre-Processing"""

data = pd.read_csv('fetal_health.csv')
data.info()
data.head()

"""Note that there are no null data values and all column Dtypes are floats. There are 21 columns which translates to 21 features to analyze. Let's now remove duplicate data entries.

"""

unduplicated_data = data.copy()
unduplicated_data.drop_duplicates(inplace=True)
print("Removed " + str(data.shape[0] - unduplicated_data.shape[0]) + " duplicates")
data = unduplicated_data

print("Total: " + str(data.shape[0]) + " samples")

data.describe().T

"""**Visualizing Fetal Health Classification Raw Data**"""

normal = data.loc[data['fetal_health'] == 1].shape[0]
suspect = data.loc[data['fetal_health'] == 2].shape[0]
pathological = data.loc[data['fetal_health'] == 3].shape[0]
total = data.fetal_health.shape[0]

print("Total count: " + str(total))
print("Normal count: " + str(normal))
print("Suspect count: " + str(suspect))
print("Pathological count: " + str(pathological))

plt.figure(figsize = (10,5))
pie_fetal_health = plt.pie([normal, suspect, pathological], labels=["Normal", "Suspect", "Pathological"], autopct="%1.0f%%")
plt.title("Fetal health count")

plt.figure(figsize = (10,5))
data['fetal_health'].value_counts().plot(figsize=(10, 5), kind="bar")
plt.title("Fetal health count")
plt.xlabel("Fetal health score")
plt.ylabel("Frequency")

plt.show()

"""Note the imbalanced dataset in terms of fetal health scoring, leading to classification inaccuracy. To better observe feature importance and correlation, a confusion matrix will be assembled to observe correlation coefficients, giving us a better idea of what the most important features are.

**Feature Analysis and Selection**
"""

feature_hist_plot = data.hist(figsize = (25,25))

"""**Confusion Matrix**

"""

plt.figure(figsize=(20, 20))
correlation_matrix = sns.heatmap(data.corr(), annot=True, cmap="Purples")

feature_correlation = data.corr()["fetal_health"].sort_values(ascending=False).to_frame()
feature_correlation.style.background_gradient(cmap=cm.Blues)

"""Note that the row we are focused on is that of "fetal_health", where we can clearly see which features are most correlated with fetal_health. Of the 21 features, the features with highest correlation is "prolongued_decelerations, "abnormal_short_term_variability", and "percentage_of_time_with_abnormal_long_term_variability".

Now that we have our correlation coefficients, let's select the most important features with the KBest algorithm.
"""

X = data.drop(["fetal_health"], axis=1)
Y = data["fetal_health"]
selected_features = SelectKBest(score_func=f_classif, k='all')

feature_fit = selected_features.fit(X, Y)
feature_scores = pd.DataFrame({"Features": X.columns,
                            "Scores": feature_fit.scores_})

feature_scores

plt.figure(figsize = (15,10))
plot = sns.barplot(data=feature_scores, x='Scores', y='Features', palette="rocket")

"""Let's now select the features with scores above the 100 threshold as our most important features and the ones that we will train our models on."""

best_features = feature_scores[feature_scores['Scores'] > 100]
best_features

best_features_array = list(best_features['Features'])
best_features_array.append('fetal_health')
data = data[best_features_array]
data.head()

"""## Scatter Matrix

Visualizes the relationships between the most important features
"""

from pandas.plotting import scatter_matrix
matrix = scatter_matrix(data, figsize=(60, 60))

"""# Dataset split (train/test)

In order to use a model, we must first scale the array of features so that they are in the same range. We will also be using the standard 70/30 train/test split.
"""

scaler = StandardScaler()
X=data.drop(["fetal_health"], axis=1)
X_df = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
X_df.info()

X_df.head()

X_df.describe().T

y=data["fetal_health"]
X_train, X_test, y_train, y_test = train_test_split(X_df, y, test_size=0.3, random_state=42)
print("X_train samples: " + str(X_train.shape[0]) + " with " + str(X_train.shape[1]) + " features")
print("Y_train samples: " + str(y_train.shape[0]))
print("X_test samples: " + str(X_test.shape[0]) + " with " + str(X_test.shape[1]) + " features")
print("Y_test samples: " + str(y_test.shape[0]))

"""# Machine Learning Classification

Here we will be using several classifiers to compare accuracy scores - we will be settling and fine-tuning the best classifier after comparing effectiveness.

## **Logistic Regression**
"""

from sklearn.linear_model import LogisticRegression

log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)
log_reg_score = log_reg.score(X_test, y_test)
print("Baseline LR Score: " + str(log_reg_score))

cv_score_lr = cross_val_score(log_reg, X_train, y_train)

print("Baseline LR CV Score: " + str(cv_score_lr.mean()))

lr_predictions = log_reg.predict(X_test)
print(classification_report(y_test, lr_predictions))

plt.subplots(figsize=(12,8))
confusion_matrix_lr = confusion_matrix(y_test, lr_predictions)
sns.heatmap(confusion_matrix_lr/np.sum(confusion_matrix_lr),annot = True, cmap="Purples")

"""## **Random Forest**"""

from sklearn.ensemble import RandomForestClassifier

random_forest = RandomForestClassifier()
random_forest.fit(X_train, y_train)
random_forest_score = random_forest.score(X_test, y_test)
print("Baseline Random Forest Score: " + str(random_forest_score))

cv_score_rf = cross_val_score(random_forest, X_train, y_train)

print("Baseline RF CV Score: " + str(cv_score_rf.mean()))

rf_predictions = random_forest.predict(X_test)
print(classification_report(y_test, rf_predictions))

plt.subplots(figsize=(12,8))
confusion_matrix_rf = confusion_matrix(y_test, rf_predictions)
sns.heatmap(confusion_matrix_rf/np.sum(confusion_matrix_rf),annot = True, cmap="Purples")

"""## **K-Nearest Neighbors**"""

from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier()
knn.fit(X_train, y_train)
knn_score = knn.score(X_test, y_test)
print("Baseline KNN Score: " + str(knn_score))

cv_score_knn = cross_val_score(knn, X_train, y_train)

print("Baseline KNN CV Score: " + str(cv_score_knn.mean()))

knn_predictions = knn.predict(X_test)
print(classification_report(y_test, knn_predictions))

plt.subplots(figsize=(12,8))
confusion_matrix_knn = confusion_matrix(y_test, knn_predictions)
sns.heatmap(confusion_matrix_knn/np.sum(confusion_matrix_knn),annot = True, cmap="Purples")

"""## **Support Vector Classifier**"""

from sklearn.svm import SVC

svc = SVC()
svc.fit(X_train, y_train)
svc_score = svc.score(X_test, y_test)
print("Baseline SVC Score: " + str(svc_score))

vc_score_svc = cross_val_score(svc, X_train, y_train)

print("Baseline SVC CV Score: " + str(vc_score_svc.mean()))

svc_predictions = svc.predict(X_test)
print(classification_report(y_test, svc_predictions))

plt.subplots(figsize=(12,8))
confusion_matrix_svc = confusion_matrix(y_test, svc_predictions)
sns.heatmap(confusion_matrix_svc/np.sum(confusion_matrix_svc),annot = True, cmap="Purples")

"""## **Linear Support Vector Classifier**

"""

from sklearn.svm import LinearSVC

linear_svc = LinearSVC()
linear_svc.fit(X_train, y_train)
linear_svc_score = linear_svc.score(X_test, y_test)
print("Baseline Linear SVC Score: " + str(linear_svc_score))

cv_score_linear_svc = cross_val_score(linear_svc, X_train, y_train)

print("Baseline Linear SVC CV Score: " + str(cv_score_linear_svc.mean()))

linear_svc_predictions = linear_svc.predict(X_test)
print(classification_report(y_test, linear_svc_predictions))

plt.subplots(figsize=(12,8))
confusion_matrix_linear_svc = confusion_matrix(y_test, linear_svc_predictions)
sns.heatmap(confusion_matrix_linear_svc/np.sum(confusion_matrix_linear_svc),annot = True, cmap="Purples")

"""## **Decision Tree**

"""

from sklearn.tree import DecisionTreeClassifier

decision_tree = DecisionTreeClassifier()
decision_tree.fit(X_train, y_train)
decision_tree_score = decision_tree.score(X_test, y_test)
print("Baseline Decision Tree Score: " + str(decision_tree_score))

cv_score_decision_tree = cross_val_score(decision_tree, X_train, y_train)

print("Baseline Decision Tree CV Score: " + str(cv_score_decision_tree.mean()))

decision_tree_predictions = decision_tree.predict(X_test)
print(classification_report(y_test, decision_tree_predictions))

plt.subplots(figsize=(12,8))
confusion_matrix_decision_tree = confusion_matrix(y_test, decision_tree_predictions)
sns.heatmap(confusion_matrix_decision_tree/np.sum(confusion_matrix_decision_tree),annot = True, cmap="Purples")

"""## **Multi-layer Perceptron (Neural Network)**

"""

from sklearn.neural_network import MLPClassifier

neural_network = MLPClassifier()
neural_network.fit(X_train, y_train)
neural_network_score = neural_network.score(X_test, y_test)
print("Baseline Multi-layer Perceptron Score: " + str(neural_network_score))

cv_score_neural_network = cross_val_score(neural_network, X_train, y_train)

print("Baseline Neural Network CV Score: " + str(cv_score_neural_network.mean()))

neural_network_predictions = neural_network.predict(X_test)
print(classification_report(y_test, neural_network_predictions))

plt.subplots(figsize=(12,8))
neural_network_decision_tree = confusion_matrix(y_test, neural_network_predictions)
sns.heatmap(neural_network_decision_tree/np.sum(neural_network_decision_tree),annot = True, cmap="Purples")

"""## **Gradient Boosting**

"""

from sklearn.ensemble import GradientBoostingClassifier

gradient_boosting = GradientBoostingClassifier()
gradient_boosting.fit(X_train, y_train)
gradient_boosting_score = gradient_boosting.score(X_test, y_test)
print("Baseline Gradient Boosting Classifier Score: " + str(gradient_boosting_score))

cv_score_gb = cross_val_score(gradient_boosting, X_train, y_train)

print("Baseline GB CV Score: " + str(cv_score_gb.mean()))

gb_predictions = gradient_boosting.predict(X_test)
print(classification_report(y_test, gb_predictions))

plt.subplots(figsize=(12,8))
gb_decision_tree = confusion_matrix(y_test, gb_predictions)
sns.heatmap(gb_decision_tree/np.sum(gb_decision_tree),annot = True, cmap="Purples")

"""## **LightGBM Classifier**

"""

from lightgbm import LGBMClassifier

light_gbm = LGBMClassifier()
light_gbm.fit(X_train, y_train)
light_gbm_score = light_gbm.score(X_test, y_test)
print("Baseline LGBM Classifer Score: " + str(light_gbm_score))

cv_score_light_gbm = cross_val_score(light_gbm, X_train, y_train)

print("Baseline LightGBM CV Score: " + str(cv_score_light_gbm.mean()))

light_gbm_predictions = light_gbm.predict(X_test)
print(classification_report(y_test, light_gbm_predictions))

plt.subplots(figsize=(12,8))
light_gbm_decision_tree = confusion_matrix(y_test, light_gbm_predictions)
sns.heatmap(light_gbm_decision_tree/np.sum(light_gbm_decision_tree),annot = True, cmap="Purples")

"""## **XGBoost Classifier**

"""

from xgboost import XGBClassifier
import xgboost

xgboost = XGBClassifier()
xgboost.fit(X_train, y_train)
xgboost_score = xgboost.score(X_test, y_test)
print("Baseline XGBoost Classifer Score: " + str(xgboost_score))

cv_score_xgboost = cross_val_score(xgboost, X_train, y_train)

print("Baseline XGBoost CV Score: " + str(cv_score_xgboost.mean()))

xgboost_predictions = xgboost.predict(X_test)
print(classification_report(y_test, xgboost_predictions))

plt.subplots(figsize=(12,8))
xgboost_decision_tree = confusion_matrix(y_test, xgboost_predictions)
sns.heatmap(xgboost_decision_tree/np.sum(xgboost_decision_tree),annot = True, cmap="Purples")

"""# **Model Scoring and Selection**"""

model_scores = pd.DataFrame({"Model": ["Logistic Regression", "Random Forest", 
                                      "K-Nearest Neighbors", "Support Vector", "Linear Support Vector",
                                      "Decision Tree", "Multi-layer Perceptron", "Gradient Boosting",
                                      "LightGBM Classifer", "XGBoost Classifier"],
                            "Scores": [log_reg_score, random_forest_score, knn_score, svc_score, linear_svc_score, decision_tree_score,
                                       neural_network_score, gradient_boosting_score, light_gbm_score, xgboost_score]})
model_scores.sort_values(by="Scores", ascending=False)

"""#Model Tuning and Optimization

## LightGBM Classifier Tuning/Optimization
"""

param_grid = {
  'learning_rate': [0.001,0.01],
  'n_estimators': [ 1000],
  'num_leaves': [12, 30,80],
  'boosting_type' : ['gbdt'],
  'objective' : ['binary'],
  'random_state' : [1],
  'colsample_bytree' : [ 0.8, 1],
  'subsample' : [0.5,0.7,0.75],
  'reg_alpha' : [0.1, 1.2],
  'reg_lambda' : [0.1, 1.2],
  'subsample_freq' : [500,1000],
  'max_depth' : [15, 30, 80]
}

cv_method = StratifiedKFold(n_splits=3)

GridSearchCV_GBM = GridSearchCV(estimator=LGBMClassifier(), 
                                param_grid=param_grid, 
                                cv=cv_method,
                                verbose=1, 
                                n_jobs=4,
                                scoring="accuracy", 
                                return_train_score=True
                                )

GridSearchCV_GBM.fit(X_train, y_train)

best_params_GBM = GridSearchCV_GBM.best_params_
best_params_GBM

best_score_GBM = GridSearchCV_GBM.best_score_
print("Optimized Grid Search GBM best score: " + str(best_score_GBM))

optimized_LGBM = LGBMClassifier(**GridSearchCV_GBM.best_params_)
optimized_LGBM.fit(X_train, y_train)

optimized_LGBM_score = optimized_LGBM.score(X_test, y_test)
print("Optimized LGBM Classifer Score: " + str(optimized_LGBM_score))

cv_score_optimized_LGBM = cross_val_score(optimized_LGBM, X_train, y_train)

print("Optimized LightGBM CV Score: " + str(cv_score_optimized_LGBM.mean()))

optimized_LGBM_predictions = optimized_LGBM.predict(X_test)
print(classification_report(y_test, optimized_LGBM_predictions))

plt.subplots(figsize=(12,8))
optimized_light_gbm_decision_tree = confusion_matrix(y_test, optimized_LGBM_predictions)
sns.heatmap(optimized_light_gbm_decision_tree/np.sum(optimized_light_gbm_decision_tree),annot = True, cmap="Purples")