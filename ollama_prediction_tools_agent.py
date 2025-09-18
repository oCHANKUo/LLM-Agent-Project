import requests
import json
import re
from datetime import datetime
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate

PREDICTION_APIS = {
    "sales": "http://127.0.0.1:5000/predict_sales_rf",
    "category": "http://127.0.0.1:5000/predict_category_trends"
}

llm = ChatOllama(model="llama3.1", temperature=0)

def parse_json_response(raw_text):
    clean_text = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(clean_text)

def handle_natural_language_prediction(user_input):
    current_year = datetime.now().year

    # Build prompt for Ollama
    prompt_template = ChatPromptTemplate.from_template("""
    You are a helpful assistant that extracts prediction requests and parameters.
    Given the user's request: "{text}", output a JSON object with:
    - "model": string, one of ["sales", "category"] depending on prediction type
    - "year": integer (default to {current_year} if not mentioned)
    - "month": integer 1-12 or null if not mentioned
    - "category": string, if relevant for category predictions, else null
    Only output valid JSON. No explanations.
    """)

    prompt_text = prompt_template.format(text=user_input, current_year=current_year)

    # Call Ollama
    response = llm.invoke(prompt_text)
    raw_text = response.content if hasattr(response, "content") else response

    # Parse JSON safely
    try:
        parsed = parse_json_response(raw_text)
    except json.JSONDecodeError:
        print("Could not parse Ollama response as JSON")
        print("Raw response:", raw_text)
        return

    # Determine which API to call
    model = parsed.get("model", "").lower()
    api_url = PREDICTION_APIS.get(model)

    if not api_url:
        print(f"No API found for model '{model}'")
        return

    # Build query parameters
    params = {"year": parsed.get("year", current_year)}
    if parsed.get("month"):
        params["month"] = parsed["month"]
    if parsed.get("category"):
        params["category"] = parsed["category"]

    # Call the API
    try:
        r = requests.get(api_url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return

    # Print prediction results
    if r.status_code == 200:
        results = r.json()
        if isinstance(results, list):
            for res in results:
                print(res)
        else:
            print(results)
    else:
        print("API returned an error:", r.json())

if __name__ == "__main__":
    print("NLP Prediction Client (type 'exit' to quit)")
    while True:
        user_input = input("\nEnter your prediction request: ")
        if user_input.lower() == "exit":
            break
        handle_natural_language_prediction(user_input)