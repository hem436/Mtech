import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from tree.base import DecisionTree
from metrics import *
from tqdm import tqdm

np.random.seed(42)
num_average_time = 20  # Number of times to run each experiment to calculate the average values

# Create some fake data to do some experiments on the runtime complexity of your decision tree algorithm. Create a dataset with N samples and M binary features. Vary M and N to plot the time taken for: 1) learning the tree, 2) predicting for test data. How do these results compare with theoretical time complexity for decision tree creation and prediction. You should do the comparison for all the four cases of decision trees.

# Function to create fake data (take inspiration from usage.py)
def create_fake_data(N: int, M: int, task: str, percent_real=0.5) -> tuple[pd.DataFrame, pd.Series]:
    """
    Function to create fake data with N samples and M binary features
    task: 'classification' or 'regression'
    """
    if task not in ['classification', 'regression']:
        raise ValueError("task must be 'classification' or 'regression'")
    # add half real and half discrete features
    X_real = pd.DataFrame(np.random.randn(N, int(M*percent_real)), columns=[f'real_{i}' for i in range(int(M*percent_real))])
    X_bin = pd.DataFrame(np.random.randint(0, 2, size=(N, M - int(M*percent_real))), columns=[f'bin_{i}' for i in range(M - int(M*percent_real))])
    X = pd.concat([X_real, X_bin], axis=1)
    if task == 'classification':
        y = pd.Series(np.random.randint(0, 2, size=N), name='target')
    else:
        y = pd.Series(np.random.rand(N), name='target')
    return X, y
# Function to calculate average time (and std) taken by fit() and predict() for different N and P for 4 different cases of DTs
def calculate_time_complexity(N_values: list[int], M_values: list[int], task: str, criterion: str, percent_real=0.5) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    fit_times = np.zeros((len(N_values), len(M_values)))
    predict_times = np.zeros((len(N_values), len(M_values)))
    fit_std = np.zeros((len(N_values), len(M_values)))
    predict_std = np.zeros((len(N_values), len(M_values)))

    for i, N in enumerate(N_values):
        for j, M in enumerate(M_values):
            X, y = create_fake_data(N, M, task, percent_real)
            dt = DecisionTree(criterion=criterion, max_depth=5)

            fit_time_list = []
            predict_time_list = []

            for _ in tqdm(range(num_average_time), desc=f"Averaging runs ({task}, {criterion})", leave=False):
                start_time = time.time()
                dt.fit(X, y)
                fit_time_list.append(time.time() - start_time)

                start_time = time.time()
                dt.predict(X)
                predict_time_list.append(time.time() - start_time)

            fit_times[i, j] = np.mean(fit_time_list)
            predict_times[i, j] = np.mean(predict_time_list)

    return fit_times, predict_times
# Function to plot the results
def plot_time_complexity(N_values: list[int], M_values: list[int], fit_times: np.ndarray, predict_times: np.ndarray,  task: str, criterion: str):
    N_grid, M_grid = np.meshgrid(M_values, N_values)

    fig = plt.figure(figsize=(14, 6))

    ax1 = fig.add_subplot(121, projection='3d')
    print(fit_times)
    ax1.plot_surface(N_grid, M_grid, fit_times, cmap='viridis', edgecolor='none')
    ax1.set_title(f'Fit Time Complexity ({task}, {criterion})')
    ax1.set_xlabel('Number of Features (M)')
    ax1.set_ylabel('Number of Samples (N)')
    ax1.set_zlabel('Time (seconds)')

    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot_surface(N_grid, M_grid, predict_times, cmap='plasma', edgecolor='none')
    ax2.set_title(f'Predict Time Complexity ({task}, {criterion})')
    ax2.set_xlabel('Number of Features (M)')
    ax2.set_ylabel('Number of Samples (N)')
    ax2.set_zlabel('Time (seconds)')

    plt.tight_layout()
    plt.show()




N_values = [20,30,40,50]
M_values = [5,10,15,20]
def run_experiments(task: str, percent_real=0.5):
    if task == 'classification':
        criterion = 'gini_index'
    else:
        criterion = 'mse'
    fit_times, predict_times = calculate_time_complexity(N_values, M_values, task, criterion,percent_real=percent_real)
    plot_time_complexity(N_values, M_values, fit_times, predict_times, task, criterion)

# Discrete input Discrete output
run_experiments('classification',0.0)
# Discrete input Real output
run_experiments('regression',0.0)
# Real input Discrete output
run_experiments('classification',1.0)
# Real input Real output
run_experiments('regression',1.0)



