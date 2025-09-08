import requests
from langchain.agents import Tool
import re

ENDPOINTS = {
    "sales":"http://localhost:5004/predict_sales_rf",
    "regional_sales":"http://localhost:5001/predict_regional_sales",
    "product":"http://localhost:5002/predict_demand",
    "customers":"http://localhost:5003/predict_customer"
}
