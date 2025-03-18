import os
from flask import Flask, request, jsonify, render_template
from google.cloud import bigquery
from google.auth import default

# Initialize Flask app
app = Flask(__name__)

# Use environment variables for configuration
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
TABLE_ID = os.getenv("TABLE_ID")

# Use default credentials for Workload Identity
credentials, _ = default()
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.get_json()

    # Prepare rows to insert
    rows_to_insert = [
        {
            "name": data["name"],
            "age": data["age"],
            "city": data["city"],
        }
    ]

    # Reference the BigQuery table
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)

    # Insert rows into the table
    errors = client.insert_rows_json(table_ref, rows_to_insert)

    if errors:
        return jsonify({"error": errors}), 400

    return jsonify({"message": "Data inserted successfully!"}), 200

@app.route('/query', methods=['GET'])
def query_data():
    # BigQuery SQL query
    query = f"""
    SELECT name, age, city
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    LIMIT 10
    """
    query_job = client.query(query)

    # Fetch query results
    results = [{"name": row.name, "age": row.age, "city": row.city} for row in query_job]

    return render_template('query.html', results=results)

if __name__ == "__main__":
    app.run(debug=True)
