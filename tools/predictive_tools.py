import requests
from langchain.agents import Tool
import re

ENDPOINTS = {
    "sales":"http://localhost:5004/predict_sales_rf",
    "regional_sales":"http://localhost:5001/predict_regional_sales",
    "product":"http://localhost:5002/predict_demand",
    "customers":"http://localhost:5003/predict_customer"
}

def call_flask_api(endpoints_url: str, user_input:str) -> str:

    year_match = re.search(r"\b(20\d{2})\b", user_input)
    month_match = re.search(r"\b(?:month )(\d{1,2})\b", user_input, re.IGNORECASE)

    params = {}
    if year_match:
        params["year"] = int(year_match.group(1))
    if month_match:
        params["month"] = int(month_match.group(1))

    try:
        response = requests.post(endpoints_url, params=params)
        data = response.json()
        if isinstance(data, list):
            return "\n".join([str(d) for d in data])
        return str(data)
    except Exception as e:
        return f"API request failed: {e}"
    
# Predictive Models Endpoint Functions
def predict_sales(user_input: str) -> str:
    return call_flask_api(ENDPOINTS["sales"], user_input)

def predict_regional_sales(user_input: str) -> str:
    return call_flask_api(ENDPOINTS["regional_sales"], user_input)

def predict_product_demand(user_input: str) -> str:
    return call_flask_api(ENDPOINTS["product"], user_input)

def predict_customer(user_input: str) -> str:
    return call_flask_api(ENDPOINTS["customers"], user_input)


tools = [
    Tool(
        name="PredictSales",
        func=predict_sales,
        description="Predict future sales via sales_prediction_model API."
    ),
    Tool(
        name="PredictProductDemand",
        func=predict_product_demand,
        description="Predict future product demand via product_demand_model API"
    ),
    Tool(
        name="PredictCustomerBehaviour",
        func=predict_customer,
        description="Predict customer behaviour"
    ),
    Tool(
        name="PredictRegionalSales",
        func=predict_regional_sales,
        description="Predict regional sales"
    )
]