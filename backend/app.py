import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify

# Initialize Flask app for Superkart Sales Predictor
superkart_api = Flask("Superkart Sales Predictor-v1")

# Load the trained sales prediction model
def load_model():
    return joblib.load("Superkart_sales_model_v2_0.joblib")

model = load_model()

# Ensure the model file is in the same directory as this script
#model = joblib.load("Superkart_sales_model_v2_0.joblib")

# Define a route for the home page
@superkart_api.get('/')
def home():
    return "Welcome to the Superkart Total Sales Prediction API!"

# Define an endpoint to predict sales for a single product in a store
@superkart_api.post('/v1/predict')
def predict_sales():
    # Get JSON data from the request
    data = request.get_json()

    # Extract relevant features from the input data
    sample = {
        'Product_Weight': data['Product_Weight'],
        'Product_Sugar_Content': data['Product_Sugar_Content'],
        'Product_Allocated_Area': data['Product_Allocated_Area'],
        'Product_Type': data['Product_Type'],
        'Product_MRP': data['Product_MRP'],
        'Store_Establishment_Year': data['Store_Establishment_Year'],
        'Store_Size': data['Store_Size'],
        'Store_Location_City_Type': data['Store_Location_City_Type'],
        'Store_Type': data['Store_Type']
    }

    # Convert the extracted data into a DataFrame
    input_data = pd.DataFrame([sample])

    # Make a sales prediction using the trained model
    # Note: Using [0] because predict returns an array
    prediction = model.predict(input_data).tolist()[0]

    # Ensure sales are not negative (common in regression artifacts)
    final_prediction = max(0, prediction)

    # Return the prediction as a JSON response
    return jsonify({'Predicted_Sales': round(final_prediction, 2)})

# Define an endpoint to predict sales for a batch of products via CSV upload
@superkart_api.post('/v1/predict_batch')
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the file into a DataFrame
    #input_df = pd.read_csv(file)

    # Rename columns to match the features the model was actually trained on
    # This addresses the KeyError due to feature name mismatch between batch data and trained model
    #input_df = input_df.rename(columns={
      #  'Store_Age_Years': 'Store_Establishment_Year',
      #  'Product_Type_Category': 'Product_Type'
    #})

    # Backup Product_Id for the output dictionary (if present)
    # If Product_Id is not in the CSV, we use row indices
    if 'Product_Id' in input_df.columns:
        ids = input_df['Product_Id'].tolist()
        # Drop ID if it wasn't used in model training
        # input_df = input_df.drop('Product_Id', axis=1)
    else:
        ids = input_df.index.tolist()

    # Make predictions for the batch data
    raw_predictions = model.predict(input_df).tolist()

    # Format predictions to be non-negative and rounded
    formatted_predictions = [round(max(0, x), 2) for x in raw_predictions]

    # Zip IDs with their respective predictions
    output_dict = dict(zip(ids, formatted_predictions))

    return jsonify(output_dict)

# Run the Flask app
if __name__ == '__main__':
    # Use port 7860 to match your Codespace configuration
    superkart_api.run(host='0.0.0.0', port=7860, debug=True)
