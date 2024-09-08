from flask import Flask, jsonify, request, render_template
import os
import pandas as pd
from sodapy import Socrata
from ai_messages import ai_analysis
#from dotenv import load_dotenv


app = Flask(__name__)

# Load environment variables from .env
#load_dotenv(dotenv_path='archtest.env') - used for local development. archtest.env is not pushed to the github repo.
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
CDC_API_ID = 'iw6q-r3ja'

# Initialize Socrata client - in the future we can get an app token for higher limits. During testing, I hit API throttling.
client = Socrata("data.cdc.gov", None)

@app.route('/')
def home():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('test.html', api_key=google_maps_api_key)

# API endpoint to fetch and filter CDC Medicare data using sodapy
@app.route('/api/medicare', methods=['GET'])
def get_medicare_data():
    # Get query parameters
    state = request.args.get('state')
    year = request.args.get('year')
    disease = request.args.get('disease')

    # Build SoQL query dynamically based on non-empty filters
    where_clause = []
    
    if state:
        where_clause.append(f"locationabbr='{state}'")
    if year:
        where_clause.append(f"year='{year}'")
    if disease:
        where_clause.append(f"topic='{disease}'")
    
    # Join the where clauses with 'AND', or leave it empty for no filters
    where_clause = " AND ".join(where_clause) if where_clause else None

    # Fetch data from the CDC API
    if where_clause:
        results = client.get(CDC_API_ID, where=where_clause, limit=2000)
    else:
        results = client.get(CDC_API_ID, limit=2000)  # Fetch all data if no filters
    
    #if client.response.status_code == 429:
    #        print("Rate limit exceeded. Try again later.")
    #        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    # Convert results to a DataFrame
    results_df = pd.DataFrame.from_records(results)

    # Convert the DataFrame back to a JSON-like format
    data = results_df.to_dict(orient='records')
    
    #OpenAI Analysis
    analysis = ai_analysis(data)
    
    # Return both data and analysis
    return jsonify({"data": data, "analysis": analysis})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
