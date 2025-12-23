import numpy as np
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
import os
from data_loader import load_and_select_features
from model import train_svm_regressor

def evaluate_model(data_path, target_column, k=10):
    # Load and select features
    X, y, selected_features = load_and_select_features(data_path, target_column, k)
    
    # Train the model
    model = train_svm_regressor(X, y)
    
    # Perform cross-validation
    scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    rmse_scores = np.sqrt(-scores)
    
    # Save performance results
    os.makedirs('results/metrics', exist_ok=True)
    with open('results/metrics/performance.txt', 'w') as f:
        f.write(f"Selected features: {selected_features}\n")
        f.write(f"Cross-validated RMSE scores: {rmse_scores}\n")
        f.write(f"Mean RMSE: {rmse_scores.mean()}\n")
        f.write(f"Standard deviation of RMSE: {rmse_scores.std()}\n")
    
    # Visualize regression results
    sns.histplot(rmse_scores, kde=True)
    plt.title('Cross-validated RMSE scores')
    plt.xlabel('RMSE')
    plt.ylabel('Frequency')
    os.makedirs('results/figures', exist_ok=True)
    plt.savefig('results/figures/rmse_scores.png')
    plt.close()

if __name__ == "__main__":
    data_path = 'path_to_gdsc_dataset.csv'  # Update this path
    target_column = 'target'  # Update this column name
    evaluate_model(data_path, target_column)
