import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tree.base import DecisionTree
from metrics import *

from sklearn.tree import DecisionTreeRegressor, plot_tree, DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
np.random.seed(42)

# Reading the data
url = 'auto+mpg/auto-mpg.data'
data = pd.read_csv(url, delim_whitespace=True, header=None,
                 names=["mpg", "cylinders", "displacement", "horsepower", "weight",
                        "acceleration", "model year", "origin", "car name"])
# Clean the above data by removing redundant columns and rows with junk values
data.drop(columns=['car name'], inplace=True)
data['horsepower'] = pd.to_numeric(data['horsepower'], errors='coerce')
data.dropna(inplace=True)
data.reset_index(drop=True, inplace=True)
x1=data.drop(columns=['mpg']).copy()
x2=data.drop(columns=['origin']).copy()
y1=data['mpg'].copy()
y2=data['origin'].copy()
print(x1.shape, x2.shape, y1.shape, y2.shape)

# Compare the performance of your model with the decision tree module from scikit learn
#1)
# Regression tree
cus_reg = DecisionTree(max_depth=3,criterion='mse')
cus_reg.fit(x1, y1)
cus_reg.plot()
predictions = cus_reg.predict(x1)
print("\n------------------------------------------------------------------------------")
print("Descision tree from scratch for regression.")
print("------------------------------------------------------------------------------")
print("root mean square error ",rmse(y1, predictions), "mean absolute error ",mae(y1, predictions))

# classification tree
cus_clf = DecisionTree(max_depth=3,criterion='gini_index')
cus_clf.fit(x2, y2)
cus_clf.plot()
predictions = cus_clf.predict(x2)
print("\n------------------------------------------------------------------------------")
print("Descision tree from scratch for classification.")
print("------------------------------------------------------------------------------")
print("Accuracy ",accuracy(y2, predictions))
print("Precision for class 1:", precision(pd.Series(predictions), y2, 1))
print("Precision for class 2:", precision(pd.Series(predictions), y2, 2))
print("Precision for class 3:", precision(pd.Series(predictions), y2, 3))
print("Recall for class 1:", recall(pd.Series(predictions), y2, 1))
print("Recall for class 2:", recall(pd.Series(predictions), y2, 2))
print("Recall for class 3:", recall(pd.Series(predictions), y2, 3))
print(confusion_matrix(y2, predictions))

#2) sklearn
# regression tree using sklearn
reg = DecisionTreeRegressor(max_depth=3,criterion='squared_error')
reg.fit(x1, y1)
predictions = reg.predict(x1)
plot_tree(reg)
print("\n------------------------------------------------------------------------------")
print("Descision tree from sklearn for regression.")
print("------------------------------------------------------------------------------")
print("root mean square error ",rmse(y1, pd.Series(predictions))**0.5, "mean absolute error ",rmse(y1, pd.Series(predictions)))

# classification tree using sklearn
clf = DecisionTreeClassifier(max_depth=3,criterion='gini')
clf.fit(x2, y2)
predictions = clf.predict(x2)
plot_tree(clf)
print("\n------------------------------------------------------------------------------")
print("Descision tree from sklearn for classification.")
print("------------------------------------------------------------------------------")
print("Accuracy ",accuracy(y2, pd.Series(predictions)))
print("Precision for class 1:", precision(pd.Series(predictions), y2, 1))
print("Precision for class 2:", precision(pd.Series(predictions), y2, 2))
print("Precision for class 3:", precision(pd.Series(predictions), y2, 3))
print("Recall for class 1:", recall(pd.Series(predictions), y2, 1))
print("Recall for class 2:", recall(pd.Series(predictions), y2, 2))
print("Recall for class 3:", recall(pd.Series(predictions), y2, 3))
print(confusion_matrix(y2, predictions))







