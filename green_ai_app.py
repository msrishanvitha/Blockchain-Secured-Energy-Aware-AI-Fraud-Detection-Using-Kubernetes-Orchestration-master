from flask import Flask, request, jsonify
import joblib
import pandas as pd
import warnings

# Suppress warnings from Prophet
warnings.filterwarnings('ignore', category=FutureWarning)

app = Flask(__name__)

# -----------------------------------------------------------------
# MODEL LOADING
# -----------------------------------------------------------------
# We load all our trained models into memory when the app starts
MODELS = {}
NODE_NAMES = ["node_a_germany", "node_b_france", "node_c_spain"]

print("Starting Green AI Flask server...")
print("Loading models into memory...")

for node_name in NODE_NAMES:
    model_filename = f"{node_name}_model.pkl"
    try:
        MODELS[node_name] = joblib.load(model_filename)
        print(f"✅ Successfully loaded model: {model_filename}")
    except FileNotFoundError:
        print(f"❌ ERROR: Model file not found: {model_filename}")
        print("Please run green_ai_train.py first to create the models.")
        MODELS[node_name] = None
    except Exception as e:
        print(f"❌ ERROR loading {model_filename}: {e}")
        MODELS[node_name] = None

# We also need to define the 'max capacity' for each region
# to calculate a meaningful 0-100 score.
# These are rough estimates based on 2023 data (in GWh/day)
# A more advanced system would get this dynamically.
NODE_MAX_GWH = {
    "node_a_germany": 1200,  # Germany's peak renewables ~1100-1200 GWh
    "node_b_france": 850,    # France's peak renewables ~800 GWh
    "node_c_spain": 750      # Spain's peak renewables ~700 GWh
}
# -----------------------------------------------------------------


@app.route('/predict', methods=['POST'])
def predict_green_energy():
    try:
        data = request.get_json()
        
        # 1. Get region and date from the request
        # Date should be in 'YYYY-MM-DD' format
        date_str = data['date']
        region = data.get('region') # e.g., "node_a_germany"

        if region not in MODELS or MODELS[region] is None:
            return jsonify({"error": f"No model loaded for region: {region}"}), 404
            
        # 2. Get the correct model for the requested region
        model = MODELS[region]

        # 3. Create the 'future' DataFrame that Prophet needs
        # Prophet's model.predict() requires a dataframe with
        # a 'ds' column containing the dates to forecast.
        future_df = pd.DataFrame({'ds': [date_str]})
        future_df['ds'] = pd.to_datetime(future_df['ds'])

        # 4. Make prediction
        # The model will forecast various things; we want 'yhat' (the prediction)
        forecast = model.predict(future_df)
        
        # Get the single predicted value
        # Prophet's 'yhat' is the forecasted GWh
        predicted_gwh = forecast['yhat'].iloc[0]
        
        # Ensure prediction is non-negative
        predicted_gwh = max(0, predicted_gwh)

        # 5. Normalize the score
        # Use the region-specific max capacity for a real score
        max_gwh = NODE_MAX_GWH.get(region, 1000) # Default to 1000 if unknown
        green_score = min(100.0, (predicted_gwh / max_gwh) * 100.0)

        return jsonify({
            "region": region,
            "predicted_renewable_gwh": round(predicted_gwh, 2),
            "green_score_percent": round(green_score, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("\nGreen AI Flask server is running on http://127.0.0.1:5001")
    # Run on a different port than the fraud model
    app.run(debug=True, port=5001)