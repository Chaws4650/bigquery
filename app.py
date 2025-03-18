import os
from flask import Flask, request, jsonify, render_template
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
client = bigquery.Client()

# Get environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
TABLE_ID = os.getenv("TABLE_ID")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.get_json()

    rows_to_insert = [
        {
            "name": data["name"],
            "age": data["age"],
            "city": data["city"],
        }
    ]

    table_ref = client.dataset(DATASET_ID, project=PROJECT_ID).table(TABLE_ID)
    errors = client.insert_rows_json(table_ref, rows_to_insert)

    if errors:
        return jsonify({"error": errors}), 400

    return jsonify({"message": "Data inserted successfully!"}), 200

@app.route('/query', methods=['GET'])
def query_data():
    query = f"""
    SELECT name, age, city
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    LIMIT 10
    """
    query_job = client.query(query)
    results = [{"name": row.name, "age": row.age, "city": row.city} for row in query_job]

    return render_template('query.html', results=results)

if __name__ == "__main__":
    app.run(debug=True)