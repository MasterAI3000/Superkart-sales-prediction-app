import streamlit as st
import pandas as pd
import requests

# --- Configuration ---
# Standard URL for frontend-to-backend communication in a Docker/Codespace network
BACKEND_URL = "http://backend:7860"

st.set_page_config(page_title="Superkart Sales Predictor", layout="wide", page_icon="🛒")

# --- UI Header ---
st.title("🛒 Superkart Sales Prediction App")
st.write("""
This app predicts the **Total Store Sales** for a particular product based on its attributes and the store's profile.
Use the form below for single estimates or the bulk upload feature for quarterly planning.
""")

st.divider()

# --- Section 1: Online Prediction (Single Product) ---
st.header(" Single Product Estimate")

# Input layout using columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Product Details")
    p_weight = st.number_input("Product Weight (kg)", min_value=0.0, value=12.0, step=0.1)
    p_mrp = st.number_input("Maximum Retail Price (MRP in $)", min_value=0.0, value=150.0, step=1.0)
    p_sugar = st.selectbox("Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    p_area = st.number_input("Allocated Display Area Ratio", min_value=0.0, max_value=1.0, value=0.05, format="%.4f")
    p_type = st.selectbox("Product Category", [
        "Meat", "Snack Foods", "Hard Drinks", "Dairy", "Canned", "Soft Drinks",
        "Health and Hygiene", "Baking Goods", "Breads", "Breakfast", "Frozen Foods",
        "Fruits and Vegetables", "Household", "Seafood", "Starchy Foods", "Others"
    ])

with col2:
    st.subheader("Store Details")
    s_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    s_year = st.number_input("Year Established", min_value=1980, max_value=2026, value=2000)
    s_city = st.selectbox("City Type", ["Tier 1", "Tier 2", "Tier 3"])
    s_type = st.selectbox("Store Category", ["Departmental Store", "Supermarket Type1", "Supermarket Type2", "Food Mart"])


# Prediction Button Logic
if st.button("Generate Sales Forecast", type="primary"):
    payload = {
        "Product_Weight": p_weight,
        "Product_Sugar_Content": p_sugar,
        "Product_Allocated_Area": p_area,
        "Product_Type": p_type,
        "Product_MRP": p_mrp,
        "Store_Establishment_Year": s_year,
        "Store_Size": s_size,
        "Store_Location_City_Type": s_city,
        "Store_Type": s_type
    }

    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload)
        if response.status_code == 200:
            final_sales = response.json()['Predicted_Sales']
            st.metric(label="Estimated Total Revenue", value=f"{final_sales:,.2f} USD")
            st.info("Estimate based on historical patterns of product performance across similar store types.")
        else:
            st.error(f"Error {response.status_code}: Unable to connect to the prediction engine.")
    except Exception as e:
        st.error(f"Connection Error: {e}")

st.divider()

# --- Section 2: Batch Prediction (CSV Upload) ---
st.header("📦 Bulk Forecast (CSV Upload)")
st.write("Upload a spreadsheet of new inventory to get a massive list of sales predictions instantly.")

uploaded_file = st.file_uploader("Upload a CSV file containing inventory data", type=["csv"])

if uploaded_file is not None:
    if st.button("Run Batch Prediction"):
        try:
            with st.spinner("Processing file..."):
                response = requests.post(f"{BACKEND_URL}/v1/predict_batch", files={"file": uploaded_file})

                if response.status_code == 200:
                    predictions = response.json()
                    st.success("Bulk processing complete!")

                    # Convert to DataFrame
                    results_df = pd.DataFrame(list(predictions.items()), columns=['Product_Id', 'Forecasted_Sales'])

                    # Display preview
                    st.dataframe(results_df, use_container_width=True)

                    # Provide Download Option
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name="superkart_bulk_forecast.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("The batch prediction service is currently unavailable.")
        except Exception as e:
            st.error(f"Failed to process batch: {e}")
