# Decision Tree Implementation - Question 3

### Showing the performance of our Decision Tree implementation on Automotive efficiency task vs standard sklearn library.
a. First we load the dataset from UCI repository and clean it. Then we split the data into features and labels for both regression and classification tasks. For regression task, we predict 'mpg' and for classification task we predict 'origin'.
```python
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
```
```text
(392, 7) (392, 7) (392,) (392,)
```

b. Compare the performance of your model with the decision tree module from scikit learn

```python
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
```
```text
Decision Tree with criterion: mse  and max_depth: 3 .

Root: ?(displacement <= 190.5) | IG: 35.2625 | Samples: 392
    ├── Y: ?(horsepower <= 70.0) | IG: 11.8674 | Samples: 222
    |   ├── Y: ?(model year_80)| IG: 3.9833 | Samples: 71
    |   |   ├── Y: Leaf | Value: 38.09166666666667 | Samples: 12
    |   |   └── N: Leaf | Value: 32.76610169491526 | Samples: 59
    |   └── N: ?(horsepower <= 84.0) | IG: 4.3139 | Samples: 151
    |       ├── Y: Leaf | Value: 28.94736842105263 | Samples: 57
    |       └── N: Leaf | Value: 24.662765957446812 | Samples: 94
    └── N: ?(horsepower <= 125.0) | IG: 5.948 | Samples: 170
        ├── Y: ?(model year_82)| IG: 3.0989 | Samples: 74
        |   ├── Y: Leaf | Value: 30.0 | Samples: 2
        |   └── N: Leaf | Value: 19.144444444444446 | Samples: 72
        └── N: ?(weight <= 4361.5) | IG: 1.3204 | Samples: 96
            ├── Y: Leaf | Value: 15.31230769230769 | Samples: 65
            └── N: Leaf | Value: 12.85483870967742 | Samples: 31

------------------------------------------------------------------------------
Descision tree from scratch for regression.
------------------------------------------------------------------------------
root mean square error  3.592817332209217 mean absolute error  2.68839859929141

------------------------------------------------------------------------------

Decision Tree with criterion: gini_index  and max_depth: 3 .

Root: ?(displacement <= 134.5) | IG: 0.1905 | Samples: 392
    ├── Y: ?(displacement <= 97.0) | IG: 0.0429 | Samples: 168
    |   ├── Y: ?(acceleration <= 19.45) | IG: 0.0763 | Samples: 77
    |   |   ├── Y: Leaf | Value: 3 | Samples: 65
    |   |   └── N: Leaf | Value: 2 | Samples: 12
    |   └── N: ?(horsepower <= 88.0) | IG: 0.089 | Samples: 91
    |       ├── Y: Leaf | Value: 1 | Samples: 58
    |       └── N: Leaf | Value: 2 | Samples: 33
    └── N: ?(displacement <= 190.5) | IG: 0.0212 | Samples: 224
        ├── Y: ?(weight <= 3071.5) | IG: 0.2198 | Samples: 54
        |   ├── Y: Leaf | Value: 1 | Samples: 46
        |   └── N: Leaf | Value: 2 | Samples: 8
        └── N: Leaf | Value: 1 | Samples: 170

------------------------------------------------------------------------------
Descision tree from scratch for classification.
------------------------------------------------------------------------------
Accuracy  0.8086734693877551
Precision for class 1: 0.8759124087591241
Precision for class 2: 0.6226415094339622
Precision for class 3: 0.676923076923077
Recall for class 1: 0.9795918367346939
Recall for class 2: 0.4852941176470588
Recall for class 3: 0.5569620253164557
confusion matrix:
[[240   3   2]
 [ 16  33  19]
 [ 18  17  44]]

------------------------------------------------------------------------------
Descision tree from sklearn for regression.
------------------------------------------------------------------------------
root mean square error  1.7954219590214415 mean absolute error  3.2235400109363908

------------------------------------------------------------------------------
Descision tree from sklearn for classification.
------------------------------------------------------------------------------
Accuracy  0.8086734693877551
Precision for class 1: 0.8759124087591241
Precision for class 2: 0.6226415094339622
Precision for class 3: 0.676923076923077
Recall for class 1: 0.9795918367346939
Recall for class 2: 0.4852941176470588
Recall for class 3: 0.5569620253164557
confusion matrix:
[[240   3   2]
 [ 16  33  19]
 [ 18  17  44]]
 ```