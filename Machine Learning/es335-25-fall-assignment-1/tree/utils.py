"""
You can add your own functions here according to your decision tree implementation.
There is no restriction on following the below template, these fucntions are here to simply help you.
"""

import pandas as pd
import numpy as np

def one_hot_encoding(X: pd.DataFrame) -> pd.DataFrame:
    """
    Function to perform one hot encoding on the input data
    """
    if not isinstance(X, pd.DataFrame):
        raise ValueError("not a pandas DataFrame")
    if X.empty:
        raise ValueError("DataFrame is empty")
    col_list = []
    for col in X.columns:
        ## check if the column is discrete using hueristic that if number of unique values is less than 10 or 5% of total values then it is discrete
        if X[col].nunique() <= 10 or X[col].nunique()/X.shape[0] <= 0.05:
            if check_ifreal(X[col]):
                continue
            col_list.append(col)
    X_encoded = pd.get_dummies(X,columns=col_list)
    return X_encoded

def check_ifreal(y: pd.Series) -> bool:
    """
    Function to check if the given series has real or discrete values
    """
    if not isinstance(y, pd.Series):
        raise ValueError("not a pandas Series")
    if pd.api.types.is_float_dtype(y):
        return True
    return False


def entropy(Y: pd.Series) -> float:
    """
    Function to calculate the entropy
    """
    if not isinstance(Y, pd.Series):
        raise ValueError("not a pandas Series")
    if Y.empty:
        raise ValueError("Series is empty")
    # formula for entropy is sum(-pi*log2(pi)) for all unique values of Y
    pi = Y.value_counts(normalize=True)
    entropy = sum(-pi * (pi.apply(lambda x: 0 if x == 0 else np.log2(x))))
    return entropy



def gini_index(Y: pd.Series) -> float:
    """
    Function to calculate the gini index
    """
    if not isinstance(Y, pd.Series):
        raise ValueError("not a pandas Series")
    if Y.empty:
        raise ValueError("Series is empty")
    # formula for gini index is 1 - sum(pi^2) for all unique values of Y 
    pi = Y.value_counts(normalize=True)
    gini = 1 - sum(pi**2)
    return gini


def information_gain(Y: pd.Series, attr: pd.Series, criterion: str) -> float:
    """
    Function to calculate the information gain using criterion (entropy, gini index or MSE)
    """
    if not isinstance(Y, pd.Series) or not isinstance(attr, pd.Series):
        raise ValueError("not a pandas Series")
    if Y.empty or attr.empty:
        raise ValueError("Series is empty")
    if len(Y) != len(attr):
        print(len(Y), len(attr))
        raise ValueError("length of y and attribute must be same")
    if criterion not in ['entropy', 'gini_index', 'mse']:
        raise ValueError("criterion must be either 'entropy' or 'gini' or 'mse'")
    if criterion == 'mse' and not check_ifreal(Y):
        raise ValueError("Y must be real valued for mse criterion")
    
    # formula for information gain is IG(Y, attr) = criteria(Y) - criteria(Y|attr), it will work for only discrete input, real and discrete outputs
    if criterion == 'entropy':
        criteria = entropy
    elif criterion == 'gini_index':
        criteria = gini_index
    else:
        criteria = lambda y: np.mean((y-np.mean(y))**2)

    SY = criteria(Y)
    WSy = 0
    for val in attr.unique():
        subset = Y[attr == val]
        WSy += (subset.size/Y.size)*criteria(subset)
    Ig = SY - WSy
    return Ig
    

def opt_split_attribute(X: pd.DataFrame, y: pd.Series, criterion, features: pd.Series):
    """
    Function to find the optimal attribute to split about.
    If needed you can split this function into 2, one for discrete and one for real valued features.
    You can also change the parameters of this function according to your implementation.

    features: pd.Series is a list of all the attributes we have to split upon

    return: attribute to split upon
    """

    # According to wheather the features are real or discrete valued and the criterion, find the attribute from the features series with the maximum information gain (entropy or varinace based on the type of output) or minimum gini index (discrete output).
    # check if y is real or discrete
    is_real = check_ifreal(y)
    if criterion == 'mse' and not is_real:
        raise ValueError("y must be real valued for mse criterion")
    
    elif criterion not in ['entropy', 'gini_index', 'mse']:
        criterion = 'entropy'

    max_ig = -float('inf')
    best_attr = None
    for attr in features:
        if attr not in X.columns:
            print(f"attribute {attr} not in X")
            continue

        if check_ifreal(X[attr]):
            if is_real:
                candidate_splits = X[attr].sort_values().rolling(2).mean().dropna().unique()
            else:
                # we will check splits at class boundaries
                # if X[attr] has na print them
                if X[attr].isna().sum() > 0:
                    print(f"attribute {attr} has NaN values {X[attr][X[attr].isna()]}")
                    continue
                sorted_idx = X[attr].argsort()
                new_x = X[attr].iloc[sorted_idx].reset_index(drop=True)
                new_y = y.iloc[sorted_idx].reset_index(drop=True)
                temp = new_y.iloc[0]
                candidate_splits = []
                for i in range(1, len(new_y)):
                    if new_y.iloc[i] != temp:
                        candidate_splits.append((new_x.iloc[i] + new_x.iloc[i-1]) / 2)
                        temp = new_y.iloc[i]

            for split in candidate_splits:
                left_mask = X[attr] <= split
                left_y = y[left_mask]
                right_y = y[~left_mask]
                # edge case when all data goes to one side
                if left_y.empty or right_y.empty:
                    continue
                ig = information_gain(y, left_mask.astype(int), criterion)
                if ig > max_ig:
                    # print(f"new best attr {attr} with split {split} and ig {ig}\n")
                    max_ig = ig
                    best_attr = (attr, split, max_ig)
        else:
            ig = information_gain(y, X[attr], criterion)
            if ig > max_ig:
                # print(f"new best attr {attr} and ig {ig}\n")
                max_ig = ig
                best_attr = (attr, None, max_ig)
    return best_attr




def split_data(X: pd.DataFrame, y: pd.Series, attribute, value=0):
    """
    Funtion to split the data according to an attribute.
    If needed you can split this function into 2, one for discrete and one for real valued features.
    You can also change the parameters of this function according to your implementation.

    attribute: attribute/feature to split upon
    value: value of that attribute to split upon

    return: splitted data(Input and output)
    """

    # Split the data based on a particular value of a particular attribute. You may use masking as a tool to split the data.
    if X.empty or y.empty:
        raise ValueError("X or y is empty")
    if attribute not in X.columns:
        raise ValueError("attribute not in X")
    if check_ifreal(X[attribute]):
        left_mask = X[attribute] <= value
        X_left = X[left_mask]
        y_left = y[left_mask]
        X_right = X[~left_mask]
        y_right = y[~left_mask]
    else:
        mask = X[attribute] == value
        X_left = X[mask]
        y_left = y[mask]
        X_right = X[~mask]
        y_right = y[~mask]
    return (X_left, y_left), (X_right, y_right)
