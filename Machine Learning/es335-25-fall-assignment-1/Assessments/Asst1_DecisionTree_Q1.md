# Decision Tree Implementation - Question 1
Output of usage.py

```
Decision Tree with criterion: mse  and max_depth: 3 .

Root: ?(1 <= -1.1939721441501923) | IG: 0.2055 | Samples: 30
    ├── Y: Leaf | Value: 2.720169166589619 | Samples: 1
    └── N: ?(4 <= 0.3865751136808898) | IG: 0.1021 | Samples: 29
        ├── Y: ?(0 <= 1.5077915869695468) | IG: 0.1375 | Samples: 21
        |   ├── Y: Leaf | Value: -0.12290235970306335 | Samples: 19
        |   └── N: Leaf | Value: 1.1403586630966704 | Samples: 2
        └── N: ?(0 <= -0.35665559739723524) | IG: 0.5169 | Samples: 8
            ├── Y: Leaf | Value: 1.6403876909353692 | Samples: 3
            └── N: Leaf | Value: 0.15533878343175386 | Samples: 5
Criteria : information_gain
RMSE:  0.5738410563649141
MAE:  0.4796223017112409

Decision Tree with criterion: mse  and max_depth: 3 .

Root: ?(1 <= -1.1939721441501923) | IG: 0.2055 | Samples: 30
    ├── Y: Leaf | Value: 2.720169166589619 | Samples: 1
    └── N: ?(4 <= 0.3865751136808898) | IG: 0.1021 | Samples: 29
        ├── Y: ?(0 <= 1.5077915869695468) | IG: 0.1375 | Samples: 21
        |   ├── Y: Leaf | Value: -0.12290235970306335 | Samples: 19
        |   └── N: Leaf | Value: 1.1403586630966704 | Samples: 2
        └── N: ?(0 <= -0.35665559739723524) | IG: 0.5169 | Samples: 8
            ├── Y: Leaf | Value: 1.6403876909353692 | Samples: 3
            └── N: Leaf | Value: 0.15533878343175386 | Samples: 5
Criteria : gini_index
RMSE:  0.5738410563649141
MAE:  0.4796223017112409

Decision Tree with criterion: information_gain  and max_depth: 3 .

Root: ?(0 <= 0.5164969924782189) | IG: 0.2845 | Samples: 30
    ├── Y: ?(1 <= 1.0083193995209832) | IG: 0.5228 | Samples: 22
    |   ├── Y: ?(2 <= -0.4498157567688338) | IG: 0.2873 | Samples: 17
    |   |   ├── Y: Leaf | Value: 1 | Samples: 5
    |   |   └── N: Leaf | Value: 1 | Samples: 12
    |   └── N: ?(2 <= -0.6496204272273054) | IG: 0.3219 | Samples: 5
    |       ├── Y: Leaf | Value: 3 | Samples: 2
    |       └── N: Leaf | Value: 4 | Samples: 3
    └── N: ?(1 <= -1.9462038896246776) | IG: 0.5436 | Samples: 8
        ├── Y: Leaf | Value: 3 | Samples: 1
        └── N: ?(4 <= -0.7267202584186923) | IG: 0.2917 | Samples: 7
            ├── Y: Leaf | Value: 4 | Samples: 2
            └── N: Leaf | Value: 2 | Samples: 5
Criteria : information_gain
Accuracy:  0.6666666666666666
Precision:  1.0
Recall:  0.5
Precision:  0.5882352941176471
Recall:  1.0
Precision:  0.6
Recall:  0.6
Precision:  0.6666666666666666
Recall:  1.0
Precision:  0
Recall:  0.0

Decision Tree with criterion: gini_index  and max_depth: 3 .

Root: ?(0 <= 0.5164969924782189) | IG: 0.0712 | Samples: 30
    ├── Y: ?(1 <= 1.0083193995209832) | IG: 0.1575 | Samples: 22
    |   ├── Y: ?(2 <= -0.7357749579035922) | IG: 0.0814 | Samples: 17
    |   |   ├── Y: Leaf | Value: 0 | Samples: 2
    |   |   └── N: Leaf | Value: 1 | Samples: 15
    |   └── N: ?(2 <= -0.6496204272273054) | IG: 0.12 | Samples: 5
    |       ├── Y: Leaf | Value: 3 | Samples: 2
    |       └── N: Leaf | Value: 4 | Samples: 3
    └── N: ?(1 <= -1.9462038896246776) | IG: 0.1652 | Samples: 8
        ├── Y: Leaf | Value: 3 | Samples: 1
        └── N: ?(4 <= -0.7267202584186923) | IG: 0.1469 | Samples: 7
            ├── Y: Leaf | Value: 4 | Samples: 2
            └── N: Leaf | Value: 2 | Samples: 5
Criteria : gini_index
Accuracy:  0.7
Precision:  1.0
Recall:  0.5
Precision:  0.6666666666666666
Recall:  1.0
Precision:  0.6
Recall:  0.6
Precision:  0.6666666666666666
Recall:  1.0
Precision:  0.5
Recall:  0.3333333333333333

Decision Tree with criterion: information_gain  and max_depth: 3 .

Root: ?(1_0)| IG: 0.4558 | Samples: 30
    ├── Y: ?(4_1)| IG: 0.4669 | Samples: 8
    |   ├── Y: Leaf | Value: 0 | Samples: 2
    |   └── N: ?(0_2)| IG: 0.3167 | Samples: 6
    |       ├── Y: Leaf | Value: 0 | Samples: 1
    |       └── N: Leaf | Value: 4 | Samples: 5
    └── N: ?(1_4)| IG: 0.43 | Samples: 22
        ├── Y: ?(2_3)| IG: 0.4669 | Samples: 8
        |   ├── Y: Leaf | Value: 1 | Samples: 5
        |   └── N: Leaf | Value: 3 | Samples: 3
        └── N: ?(4_3)| IG: 0.5528 | Samples: 14
            ├── Y: Leaf | Value: 1 | Samples: 3
            └── N: Leaf | Value: 2 | Samples: 11
Criteria : information_gain
Accuracy:  0.6666666666666666
Precision:  0.6666666666666666
Recall:  0.2857142857142857
Precision:  0.8
Recall:  1.0
Precision:  0.875
Recall:  0.7777777777777778
Precision:  0.45454545454545453
Recall:  1.0
Precision:  0.6666666666666666
Recall:  0.4

Decision Tree with criterion: gini_index  and max_depth: 3 .

Root: ?(1_4)| IG: 0.1125 | Samples: 30
    ├── Y: ?(2_3)| IG: 0.2083 | Samples: 8
    |   ├── Y: Leaf | Value: 1 | Samples: 5
    |   └── N: ?(0_4)| IG: 0.4444 | Samples: 3
    |       ├── Y: Leaf | Value: 1 | Samples: 1
    |       └── N: Leaf | Value: 3 | Samples: 2
    └── N: ?(1_0)| IG: 0.0999 | Samples: 22
        ├── Y: ?(4_1)| IG: 0.1354 | Samples: 8
        |   ├── Y: Leaf | Value: 0 | Samples: 2
        |   └── N: Leaf | Value: 4 | Samples: 6
        └── N: ?(4_3)| IG: 0.1357 | Samples: 14
            ├── Y: Leaf | Value: 1 | Samples: 3
            └── N: Leaf | Value: 2 | Samples: 11
Criteria : gini_index
Accuracy:  0.6666666666666666
Precision:  0.5
Recall:  0.14285714285714285
Precision:  0.6666666666666666
Recall:  1.0
Precision:  0.8888888888888888
Recall:  0.8888888888888888
Precision:  0.45454545454545453
Recall:  1.0
Precision:  1.0
Recall:  0.4

Decision Tree with criterion: mse  and max_depth: 3 .

Root: ?(2_1)| IG: 0.1253 | Samples: 30
    ├── Y: ?(1_1)| IG: 0.6214 | Samples: 6
    |   ├── Y: Leaf | Value: -2.4716445001272893 | Samples: 1
    |   └── N: ?(0_1)| IG: 0.7071 | Samples: 5
    |       ├── Y: Leaf | Value: -2.038124535177854 | Samples: 1
    |       └── N: Leaf | Value: 0.06403871866108457 | Samples: 4
    └── N: ?(1_4)| IG: 0.1133 | Samples: 24
        ├── Y: ?(2_2)| IG: 0.4384 | Samples: 4
        |   ├── Y: Leaf | Value: 0.5463131784121966 | Samples: 3
        |   └── N: Leaf | Value: 2.075400798645439 | Samples: 1
        └── N: ?(3_0)| IG: 0.087 | Samples: 20
            ├── Y: Leaf | Value: 0.5362663596948137 | Samples: 5
            └── N: Leaf | Value: -0.14488682475431275 | Samples: 15
Criteria : information_gain
RMSE:  0.5944858156901102
MAE:  0.48611654327295073

Decision Tree with criterion: mse  and max_depth: 3 .

Root: ?(2_1)| IG: 0.1253 | Samples: 30
    ├── Y: ?(1_1)| IG: 0.6214 | Samples: 6
    |   ├── Y: Leaf | Value: -2.4716445001272893 | Samples: 1
    |   └── N: ?(0_1)| IG: 0.7071 | Samples: 5
    |       ├── Y: Leaf | Value: -2.038124535177854 | Samples: 1
    |       └── N: Leaf | Value: 0.06403871866108457 | Samples: 4
    └── N: ?(1_4)| IG: 0.1133 | Samples: 24
        ├── Y: ?(2_2)| IG: 0.4384 | Samples: 4
        |   ├── Y: Leaf | Value: 0.5463131784121966 | Samples: 3
        |   └── N: Leaf | Value: 2.075400798645439 | Samples: 1
        └── N: ?(3_0)| IG: 0.087 | Samples: 20
            ├── Y: Leaf | Value: 0.5362663596948137 | Samples: 5
            └── N: Leaf | Value: -0.14488682475431275 | Samples: 15
Criteria : gini_index
RMSE:  0.5944858156901102
MAE:  0.48611654327295073
```

## Performance on generated dataset
We generated the dataset using the following code:

```python
from sklearn.datasets import make_classification
X, y = make_classification(
    n_features=2, n_redundant=0, n_informative=2, random_state=1, n_clusters_per_class=2, class_sep=0.5)

# For plotting
import matplotlib.pyplot as plt
plt.scatter(X[:, 0], X[:, 1], c=y)
```

### Results
- The dataset was split into 70% training and 30% testing.
- Accuracy, per-class precision, and recall were calculated using the implemented decision tree.

## Cross-Validation
- 5-fold cross-validation was performed.
- Nested cross-validation was used to find the optimum depth of the tree.
