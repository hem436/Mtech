"""
Test script to verify the optimized decision tree implementation
"""
import pandas as pd
import numpy as np
import time
from tree.base import DecisionTree

# Generate sample data for testing
np.random.seed(42)
n_samples = 1000
n_features = 10

# Create mixed data (real and discrete)
X = pd.DataFrame({
    f'real_{i}': np.random.normal(0, 1, n_samples) for i in range(5)
})
X.update({
    f'discrete_{i}': np.random.choice(['A', 'B', 'C'], n_samples) for i in range(5)
})

# Create target variable
y = pd.Series(np.random.choice([0, 1], n_samples))

print("Testing optimized Decision Tree...")
print(f"Dataset size: {n_samples} samples, {n_features} features")

# Test classification
start_time = time.time()
clf = DecisionTree(criterion="information_gain", max_depth=5)
clf.fit(X, y)
fit_time = time.time() - start_time

start_time = time.time()
predictions = clf.predict(X)
predict_time = time.time() - start_time

print(f"Fit time: {fit_time:.4f} seconds")
print(f"Predict time: {predict_time:.4f} seconds")
print(f"Accuracy: {(predictions == y).mean():.4f}")

# Test regression
y_reg = pd.Series(np.random.normal(0, 1, n_samples))

start_time = time.time()
reg = DecisionTree(criterion="mse", max_depth=5)
reg.fit(X, y_reg)
reg_fit_time = time.time() - start_time

start_time = time.time()
reg_predictions = reg.predict(X)
reg_predict_time = time.time() - start_time

print(f"\nRegression fit time: {reg_fit_time:.4f} seconds")
print(f"Regression predict time: {reg_predict_time:.4f} seconds")
print(f"RMSE: {np.sqrt(np.mean((reg_predictions - y_reg)**2)):.4f}")

print("\nOptimization completed successfully!")
