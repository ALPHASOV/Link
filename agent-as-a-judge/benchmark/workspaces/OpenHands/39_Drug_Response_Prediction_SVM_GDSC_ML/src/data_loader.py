import pandas as pd
from sklearn.feature_selection import SelectKBest, f_regression

def load_and_select_features(data_path, target_column, k=10):
    # Load the dataset
    data = pd.read_csv(data_path)
    
    # Separate features and target
    X = data.drop(columns=[target_column])
    y = data[target_column]
    
    # Perform feature selection
    selector = SelectKBest(score_func=f_regression, k=k)
    X_selected = selector.fit_transform(X, y)
    
    # Get selected feature names
    selected_features = X.columns[selector.get_support()]
    
    return X_selected, y, selected_features

if __name__ == "__main__":
    data_path = 'path_to_gdsc_dataset.csv'  # Update this path
    target_column = 'target'  # Update this column name
    X_selected, y, selected_features = load_and_select_features(data_path, target_column)
    print(f"Selected features: {selected_features}")
