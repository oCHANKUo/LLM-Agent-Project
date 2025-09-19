import requests
import json
import re
from datetime import datetime
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate

PREDICTION_APIS = {
    "sales": "http://127.0.0.1:5004/predict_sales_rf",
    "regional_sales": "http://127.0.0.1:5001/predict_regional_sales"  # Change this API endpoint
}

llm = ChatOllama(model="llama3.1", temperature=0)

def parse_json_response(raw_text):
    clean_text = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(clean_text)

def handle_natural_language_prediction(user_input):
    current_year = datetime.now().year

    # Build prompt for Ollama
    prompt_template = ChatPromptTemplate.from_template("""
    You are a strict JSON generator.
    You will extract prediction requests and return ONLY a JSON object with the following fields:
    - "model": one of ["sales", "regional_sales"]
    - "year": integer (default to {current_year} if not mentioned)
    - "month": integer 1-12 or null if not mentioned
    - "territory": string if relevant for regional_sales, else null

    Rules:
    - Always output valid JSON.
    - No explanations or extra text.
    - Do not wrap in markdown code fences.
    User request: "{text}"
    """)

    prompt_text = prompt_template.format(text=user_input, current_year=current_year)

    response = llm.invoke(prompt_text)
    raw_text = response.content if hasattr(response, "content") else response

    try:
        parsed = parse_json_response(raw_text)
    except json.JSONDecodeError:
        print("Could not parse Ollama response as JSON")
        print("Raw response:", raw_text)
        return

    model = parsed.get("model", "").lower()
    api_url = PREDICTION_APIS.get(model)

    if not api_url:
        print(f"No API found for model '{model}'")
        return

    params = {"year": parsed.get("year", current_year)}
    if parsed.get("month"):
        params["month"] = parsed["month"]
    if model == "regional_sales" and parsed.get("territory"):
        params["TerritoryName"] = parsed["territory"]

    try:
        r = requests.get(api_url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return

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