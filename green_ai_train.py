import pandas as pd
from prophet import Prophet
import joblib
import warnings
import os
import subprocess
import sys

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)

print("Starting Green AI model training (Dynamic Columns version)...")

# -----------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------

# 1. Define the files we downloaded
NODE_FILES = {
    "node_a_germany": "germany_data.csv",
    "node_b_france": "france_data.csv",
    "node_c_spain": "spain_data.csv"
}

# 2. Define the keywords to search for in column names
RENEWABLE_KEYWORDS = ['Solar', 'Wind', 'Hydro', 'Biomass', 'Geothermal']
TIME_COLUMN_NAME = 'MTU (CET/CEST)' # <-- FIX 1
# -----------------------------------------------------------------

def clean_data_for_prophet(filepath):
    """
    Loads an ENTSO-E CSV, dynamically sums renewables, and formats for Prophet.
    """
    if not os.path.exists(filepath):
        print(f"❌ ERROR: File not found: {filepath}")
        print("Please make sure you downloaded the files from ENTSO-E and named them correctly.")
        return None
        
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"❌ ERROR reading {filepath}: {e}")
        return None
        
    print(f"\nProcessing {filepath}...")

    # 1. Convert 'Time' column to datetime
    if TIME_COLUMN_NAME not in df.columns:
        print(f"❌ ERROR: Time column '{TIME_COLUMN_NAME}' not found in {filepath}.")
        print(f"   Available columns are: {list(df.columns)}")
        return None
        
    try:
        # Parse the start time of the interval (e.g., 'DD.MM.YYYY HH:mm - ...')
        df['ds_str'] = df[TIME_COLUMN_NAME].apply(lambda x: x.split(' - ')[0])
        df['ds'] = pd.to_datetime(df['ds_str'], format='%d.%m.%Y %H:%M')
    except Exception as e:
        print(f"❌ ERROR: Could not parse time column '{TIME_COLUMN_NAME}'. Format may be different. Error: {e}")
        return None
    
    # 2. Dynamically find and sum renewable sources
    
    # Find columns that represent *actual* generation (must contain "Current")
    actual_gen_cols = [col for col in df.columns if 'Current' in col]
    
    total_renewable_mw = pd.Series([0] * len(df))
    found_cols_count = 0
    
    print("  Searching for renewable source columns...")
    for col in actual_gen_cols:
        # Check if this "Current" column is also a renewable source
        if any(keyword in col for keyword in RENEWABLE_KEYWORDS):
            print(f"  ...Found and summing: {col}")
            found_cols_count += 1
            # Convert numeric columns, forcing errors (like 'n/e') to NaN
            numeric_col = pd.to_numeric(df[col], errors='coerce')
            # Fill any NaNs (missing data or 'n/e') with 0
            total_renewable_mw = total_renewable_mw.add(numeric_col.fillna(0))
            
    if found_cols_count == 0:
        print(f"❌ ERROR: No 'Current' renewable columns found in {filepath}.")
        print("   Please check your CSV headers or RENEWABLE_KEYWORDS list.")
        return None
    else:
        print(f"  Successfully summed {found_cols_count} renewable source columns.")
            
    df['y'] = total_renewable_mw # 'y' is the target for Prophet
    
    # 3. Resample from hourly/quarterly to Daily (D)
    # We sum the MW values to get a daily total (MWh)
    # and divide by 1000 to get GWh
    df = df[['ds', 'y']].set_index('ds')
    df_daily = df.resample('D').sum()
    df_daily['y'] = df_daily['y'] / 1000.0
    
    # Reset index to get 'ds' back as a column for Prophet
    df_daily = df_daily.reset_index()
    
    print(f"  Successfully processed {len(df_daily)} days of data.")
    return df_daily

# --- Main execution ---
if __name__ == "__main__":
    
    # First, install Prophet if you haven't
    try:
        import prophet
    except ImportError:
        print("Prophet library not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "prophet"])
    
    for node_name, filepath in NODE_FILES.items():
        print(f"\n--- Training model for {node_name} ---")
        
        # 1. Load and clean data
        df_prophet = clean_data_for_prophet(filepath)
        
        if df_prophet is None:
            print(f"Skipping model training for {node_name} due to data error.")
            continue
            
        # 2. Train the model
        print("Initializing Prophet model...")
        model = Prophet(seasonality_mode='multiplicative', 
                          yearly_seasonality=True, 
                          weekly_seasonality=True,
                          daily_seasonality=False)
        
        print(f"Fitting model for {node_name}... (This may take a minute)")
        model.fit(df_prophet)
        
        # 3. Save the trained model
        model_filename = f"{node_name}_model.pkl"
        joblib.dump(model, model_filename)
        
        print(f"✅ Success! Model saved as '{model_filename}'")
        
    print("\n--- All models trained successfully. ---")

