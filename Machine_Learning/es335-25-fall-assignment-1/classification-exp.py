import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tree.base import DecisionTree
from metrics import *
from sklearn.datasets import make_classification

np.random.seed(42)

# Code given in the question
X, y = make_classification(
    n_features=2, n_redundant=0, n_informative=2, random_state=1, n_clusters_per_class=2, class_sep=0.5)

# Write the code for Q2 a) and b) below. Show your results.
data = pd.DataFrame(X, columns=['f1', 'f2'])
Y= pd.Series(y)
X_train, X_test = data.iloc[:70], data.iloc[70:].reset_index(drop=True)
print(X_train.shape, X_test.shape)
y_train, y_test = Y.iloc[:70], Y.iloc[70:].reset_index(drop=True)
dt = DecisionTree(criterion='gini_index', max_depth=5)
dt.fit(X_train, y_train)
dt.plot()

# a) accuracy and per class precision, recall 
predictions = dt.predict(X_test)
print("Accuracy:", accuracy(pd.Series(predictions), y_test))
print("Precision for class 0:", precision(pd.Series(predictions), y_test, 0))
print("Precision for class 1:", precision(pd.Series(predictions), y_test, 1))
print("Recall for class 0:", recall(pd.Series(predictions), y_test, 0))
print("Recall for class 1:", recall(pd.Series(predictions), y_test, 1))


# b) showing 5 fold cross-validation error vs max_depth (1 to 10) without using sklearn
depths = list(range(1, 11))
cv_errors = []
for depth in depths:
    fold_errors = []
    fold_size = len(X_train) // 5
    for i in range(5):
        X_val = X_train.iloc[i*fold_size:(i+1)*fold_size].reset_index(drop=True)
        y_val = y_train.iloc[i*fold_size:(i+1)*fold_size].reset_index(drop=True)
        X_tr = pd.concat([X_train.iloc[:i*fold_size], X_train.iloc[(i+1)*fold_size:]]).reset_index(drop=True)
        y_tr = pd.concat([y_train.iloc[:i*fold_size], y_train.iloc[(i+1)*fold_size:]]).reset_index(drop=True)
        
        model = DecisionTree(criterion='gini_index', max_depth=depth)
        model.fit(X_tr, y_tr)
        val_predictions = model.predict(X_val)
        fold_errors.append(1 - accuracy(pd.Series(val_predictions), y_val))
    cv_errors.append(np.mean(fold_errors))

plt.plot(depths, cv_errors, marker='o')
plt.xlabel('Max Depth')
plt.ylabel('5-Fold CV Error')
plt.title('5-Fold Cross-Validation Error vs Max Depth')
plt.xticks(depths)
plt.grid()

optimal_depth = depths[np.argmin(cv_errors)]
print("Optimal max_depth:", optimal_depth)
# Training error and test error for optimal max_depth
optimal_model = DecisionTree(criterion='gini_index', max_depth=optimal_depth)
optimal_model.fit(X_train, y_train)
train_predictions = optimal_model.predict(X_train)
test_predictions = optimal_model.predict(X_test)
print("Training Error:", 1 - accuracy(pd.Series(train_predictions), y_train))
print("Test Error:", 1 - accuracy(pd.Series(test_predictions), y_test))
## accuracy, precision, recall for optimal max_depth
print("Test Accuracy:", round(accuracy(pd.Series(test_predictions), y_test), 5))
print("Test Precision for class 0:", round(precision(pd.Series(test_predictions), y_test, 0), 5))
print("Test Precision for class 1:", round(precision(pd.Series(test_predictions), y_test, 1), 5))
print("Test Recall for class 0:", round(recall(pd.Series(test_predictions), y_test, 0), 5))
print("Test Recall for class 1:", round(recall(pd.Series(test_predictions), y_test, 1), 5))
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.scatter(X_test.iloc[:,0],X_test.iloc[:,1], c=test_predictions, marker='o')
plt.title('Predictions')
plt.subplot(1, 2, 2)
plt.scatter(X_test.iloc[:,0],X_test.iloc[:,1], c=y_test, marker='o')
plt.title('True Labels')
plt.show()
