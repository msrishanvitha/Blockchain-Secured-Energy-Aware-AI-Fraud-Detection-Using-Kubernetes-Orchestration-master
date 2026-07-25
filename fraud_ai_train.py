import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

def generate_synthetic_data(n_samples=50000):
    """Generates a synthetic transaction dataset."""
    print(f"Generating {n_samples} synthetic transactions...")
    
    # Create normal transactions
    normal_amounts = np.random.lognormal(mean=3.5, sigma=1, size=int(n_samples * 0.99))
    normal_times = np.random.normal(loc=14.0, scale=4.0, size=int(n_samples * 0.99))
    normal_types = np.random.choice(['ONLINE', 'IN-STORE', 'ATM'], size=int(n_samples * 0.99), p=[0.5, 0.4, 0.1])
    
    # Create fraudulent transactions (anomalies)
    n_fraud = n_samples - len(normal_amounts)
    fraud_amounts = np.random.lognormal(mean=6.5, sigma=0.5, size=n_fraud) # Much higher amounts
    fraud_times = np.random.uniform(low=0.0, high=23.9, size=n_fraud) # At all times
    fraud_types = np.random.choice(['ONLINE', 'IN-STORE', 'ATM'], size=n_fraud, p=[0.8, 0.1, 0.1]) # Mostly online
    
    # Combine
    amounts = np.concatenate([normal_amounts, fraud_amounts])
    times = np.concatenate([normal_times, fraud_times])
    types = np.concatenate([normal_types, fraud_types])
    
    # Clip values to be realistic
    amounts = np.clip(amounts, 0.5, 10000)
    times = np.clip(times, 0.0, 23.9)
    
    df = pd.DataFrame({
        'Amount': amounts,
        'TimeOfDay': times, # 0.0 - 23.9
        'TransactionType': types
    })
    
    print("Data generation complete.")
    return df

# --- Main execution ---
if __name__ == "__main__":
    print("Starting Fraud AI model training...")
    
    # 1. Get Data
    X = generate_synthetic_data()
    
    # 2. Define preprocessing
    # We need to one-hot-encode the 'TransactionType'
    categorical_features = ['TransactionType']
    numeric_features = ['Amount', 'TimeOfDay']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough' # Keep 'Amount' and 'TimeOfDay'
    )
    
    # 3. Define the model
    # IsolationForest is great for anomaly detection.
    # 'contamination' is the % of data we expect to be fraudulent.
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    
    # 4. Create and train the full pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    print("Training IsolationForest model...")
    pipeline.fit(X)
    print("Model training complete.")
    
    # 5. Save the pipeline
    model_filename = 'fraud_model.pkl'
    joblib.dump(pipeline, model_filename)
    
    print(f"✅ Fraud detection model saved as '{model_filename}'")
