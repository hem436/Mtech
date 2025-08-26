from typing import Union
import pandas as pd


def accuracy(y_hat: pd.Series, y: pd.Series) -> float:
    """
    Function to calculate the accuracy
    """

    """
    The following assert checks if sizes of y_hat and y are equal.
    Students are required to add appropriate assert checks at places to
    ensure that the function does not fail in corner cases.
    """
    if not isinstance(y_hat, pd.Series) or not isinstance(y, pd.Series):
        raise ValueError("not a pandas Series")
    if y_hat.empty or y.empty:
        raise ValueError("y or y_predicion is empty")
    
    assert y_hat.size == y.size
    
    return (y_hat == y).mean()


def precision(y_hat: pd.Series, y: pd.Series, cls: Union[int, str]) -> float:
    """
    Function to calculate the precision
    """
    if not isinstance(y_hat, pd.Series) or not isinstance(y, pd.Series):
        raise ValueError("not a pandas Series")
    if y_hat.empty or y.empty:
        raise ValueError("y or y_predicion is empty")
    assert y_hat.size == y.size
    tp = (y_hat == cls) & (y == cls)
    fp = (y_hat == cls) & (y != cls)
    if tp.sum()+fp.sum() ==0:
        return 0
    return tp.sum()/(tp.sum()+fp.sum())


def recall(y_hat: pd.Series, y: pd.Series, cls: Union[int, str]) -> float:
    """
    Function to calculate the recall
    """
    if not isinstance(y_hat, pd.Series) or not isinstance(y, pd.Series):
        raise ValueError("not a pandas Series")
    if y_hat.empty or y.empty:
        raise ValueError("y or y_predicion is empty")
    assert y_hat.size == y.size
    tp = (y_hat == cls) & (y == cls)
    fn = (y_hat != cls) & (y == cls)
    if tp.sum()+fn.sum() ==0:
        return 0
    return tp.sum()/(tp.sum()+fn.sum())


def rmse(y_hat: pd.Series, y: pd.Series) -> float:
    """
    Function to calculate the root-mean-squared-error(rmse)
    """
    if not isinstance(y_hat, pd.Series) or not isinstance(y, pd.Series):
        raise ValueError("not a pandas Series")
    if y_hat.empty or y.empty:
        raise ValueError("y or y_predicion is empty")
    if not (pd.api.types.is_integer_dtype(y) or pd.api.types.is_float_dtype(y)):
        raise ValueError("y must be real valued")
    if not (pd.api.types.is_integer_dtype(y_hat) or pd.api.types.is_float_dtype(y_hat)):
        raise ValueError("y_hat must be real valued")
    assert y_hat.size == y.size
    return ((y_hat - y)**2).mean()**0.5


def mae(y_hat: pd.Series, y: pd.Series) -> float:
    """
    Function to calculate the mean-absolute-error(mae)
    """
    if not isinstance(y_hat, pd.Series) or not isinstance(y, pd.Series):
        raise ValueError("not a pandas Series")
    if y_hat.empty or y.empty:
        raise ValueError("y or y_predicion is empty")
    if not (pd.api.types.is_integer_dtype(y) or pd.api.types.is_float_dtype(y)):
        raise ValueError("y must be real valued")
    if not (pd.api.types.is_integer_dtype(y_hat) or pd.api.types.is_float_dtype(y_hat)):
        raise ValueError("y_hat must be real valued")
    assert y_hat.size == y.size
    return (y_hat - y).abs().mean()
