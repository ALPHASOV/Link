from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def train_svm_regressor(X, y):
    # Create a pipeline with standard scaler and SVM regressor
    model = make_pipeline(StandardScaler(), SVR(kernel='linear'))
    
    # Train the model
    model.fit(X, y)
    
    return model
