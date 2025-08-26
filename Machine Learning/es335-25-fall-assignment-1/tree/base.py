"""
The current code given is for the Assignment 1.
You will be expected to use this to make trees for:
> discrete input, discrete output
> real input, real output
> real input, discrete output
> discrete input, real output
"""
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tree.utils import *

np.random.seed(42)


@dataclass
class DecisionTree:
    criterion: Literal["information_gain", "gini_index"]  # criterion won't be used for regression
    max_depth: int  

    
    def __init__(self, criterion, max_depth=3):
        self.criterion = criterion
        self.max_depth = max_depth
        self.tree = None

    class treeNode:
        def __init__(self, attribute=None, threshold=None, left=None, right=None, value=None, ig=None, n_samples=0):
            self.attribute = attribute  
            self.threshold = threshold  
            self.ig = ig                # node info gain
            self.left = left            #left child node
            self.right = right          #right child node
            self.value = value          #class label dict for classification or mean value for regression
            self.n_samples = n_samples       #number of samples at the node
            self.is_leaf = True if attribute is None else False

        def is_leaf(self):
            return self.is_leaf

    def fit(self, X: pd.DataFrame, y: pd.Series) -> treeNode:
        """
        Function to train and construct the decision tree
        """

        # If you wish your code can have cases for different types of input and output data (discrete, real)
        # Use the functions from utils.py to find the optimal attribute to split upon and then construct the tree accordingly.
        # You may(according to your implemetation) need to call functions recursively to construct the tree. 
        if not isinstance(X, pd.DataFrame) or not isinstance(y, pd.Series):
            raise ValueError("X must be a pandas DataFrame and y must be a pandas Series")
        if X.empty or y.empty:
            raise ValueError("X or y is empty")
        
        X=one_hot_encoding(X)

        features = X.columns
        if check_ifreal(y):
            self.criterion = 'mse'

        if self.max_depth <= 0:
            self.tree = DecisionTree.treeNode(value=y.mode()[0], n_samples=len(y))
        else:
            self.tree = self._build_tree(X, y, features, depth=0)
        return self.tree
    
    def _build_tree(self, X, y, features, depth):
        """
        X: input dataframe
        y: target series
        depth: current depth of tree
        """
        # stopping conditions
        if len(y) == 1:
            return DecisionTree.treeNode(value=y.iloc[0], n_samples=1)

        # best attribute to split on
        split = opt_split_attribute(X, y, self.criterion, features)
        if split is None:
            return DecisionTree.treeNode(value=y.mode()[0], n_samples=len(y))
        best_attr, threshold, ig = split
        # print(f"best attr {best_attr} at depth {depth}")
        
        # create subtrees for discrete y
        if not check_ifreal(y):

            if len(features) == 0 or depth == self.max_depth:
                return DecisionTree.treeNode(value=y.mode()[0], n_samples=len(y))
            if threshold is not None:
                # print("1st: {features}")

                left_mask = X[best_attr] <= threshold
                right_mask = X[best_attr] > threshold
                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    return DecisionTree.treeNode(value=y.mode()[0], n_samples=len(y))
                left_node = self._build_tree(X[left_mask], y[left_mask], features, depth+1)
                right_node = self._build_tree(X[right_mask], y[right_mask], features, depth+1)

                return DecisionTree.treeNode(attribute=best_attr, threshold=threshold, left=left_node,\
                                              right=right_node, value=y.value_counts().to_dict(), n_samples=len(y),ig=ig)
            else:
                # print("2nd: {features}")

                left_mask = X[best_attr] == 1
                right_mask = X[best_attr] == 0
                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    return DecisionTree.treeNode(value=y.mode()[0], n_samples=len(y))
                left_node = self._build_tree(X[left_mask], y[left_mask], features.drop(best_attr), depth+1)
                right_node = self._build_tree(X[right_mask], y[right_mask], features.drop(best_attr), depth+1)
                return DecisionTree.treeNode(attribute=best_attr, left=left_node, right=right_node,\
                                              value=y.value_counts().to_dict() , n_samples=len(y),ig=ig)
        else:
            # create subtrees for real y
            if len(features) == 0 or depth == self.max_depth:
                return DecisionTree.treeNode(value=y.mean(), n_samples=len(y))
            if threshold is not None:
                left_mask = X[best_attr] <= threshold
                right_mask = X[best_attr] > threshold
                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    return DecisionTree.treeNode(value=y.mean(), n_samples=len(y))
                left_node = self._build_tree(X[left_mask], y[left_mask], features, depth+1)
                right_node = self._build_tree(X[right_mask], y[right_mask], features, depth+1)
                return DecisionTree.treeNode(attribute=best_attr, threshold=threshold, left=left_node,\
                                              right=right_node, value=y.mean(), n_samples=len(y),ig=ig)
            else:
                left_mask = X[best_attr] == 1
                right_mask = X[best_attr] == 0
                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    return DecisionTree.treeNode(value=y.mean(), n_samples=len(y))
                left_node = self._build_tree(X[left_mask], y[left_mask], features.drop(best_attr), depth+1)
                right_node = self._build_tree(X[right_mask], y[right_mask], features.drop(best_attr), depth+1)
                return DecisionTree.treeNode(attribute=best_attr, left=left_node, right=right_node,\
                                              value=y.mean(), n_samples=len(y),ig=ig)
 

        


    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Funtion to run the decision tree on test inputs
        """

        # Traverse the tree you constructed to return the predicted values for the given test inputs.
        if self.tree is None:
            raise ValueError("Tree is not trained yet. Please call fit() before predict().")
        if not isinstance(X, pd.DataFrame) or X.empty:
            raise ValueError("invalid test data")
        X=one_hot_encoding(X)
        node = self.tree
        y_pred = []
        for _, row in X.iterrows():
            node = self.tree
            while not node.is_leaf:
                if node.attribute not in row.index:
                        raise ValueError(f"attribute {node.attribute} not in test data")
                if node.threshold is not None:
                    if row[node.attribute] <= node.threshold:
                        node = node.left
                    else:
                        node = node.right
                else:
                    if row[node.attribute] == 1:
                        node = node.left
                    else:
                        node = node.right
            y_pred.append(node.value)
        return pd.Series(y_pred)        


    def plot(self) -> None:
        """
        Function to plot the tree


        Output Example:
        ?(X1 > 4)
            Y: ?(X2 > 7)
                Y: Class A
                N: Class B
            N: Class C
        Where Y => Yes and N => No
        """
        print("\nDecision Tree with criterion:", self.criterion, " and max_depth:", self.max_depth, ".\n")

        def _plot_tree(node, prefix="", branch=None, is_left=True, is_root=True):
            if is_root:
                tag = "Root: "
            elif branch == "Y":
                tag = "Y: "
            elif branch == "N":
                tag = "N: "
            else:
                tag = ""

            connector = "├── " if is_left and not is_root else ("└── " if not is_left and not is_root else "")

            if node is None:
                print(prefix + connector + tag + "[None]")
                return

            if getattr(node, 'is_leaf', False):
                print(prefix + connector + tag + f"Leaf | Value: {node.value} | Samples: {node.n_samples}")
            else:
                if getattr(node, 'threshold', None) is not None:
                    print(prefix + connector + tag + f"?({node.attribute} <= {node.threshold}) | IG: {round(node.ig,4)} | Samples: {node.n_samples}")
                else:
                    print(prefix + connector + tag + f"?({node.attribute})| IG: {round(node.ig,4)} | Samples: {node.n_samples}")

                child_prefix = prefix + ("|   " if is_left and not is_root else "    ")
                _plot_tree(node.left, child_prefix, branch="Y", is_left=True, is_root=False)
                _plot_tree(node.right, child_prefix, branch="N", is_left=False, is_root=False)

        if self.tree is not None:
            _plot_tree(self.tree)
        else:
            print("Tree is not trained yet.")

