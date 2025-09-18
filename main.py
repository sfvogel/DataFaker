import json
import os
import random
from datetime import datetime, timedelta
from faker import Faker
import requests # Neu hinzugefügt

# Initialize Faker with a specific seed for reproducible data
Faker.seed(42)
fake = Faker()

# Define a list of possible authors
AUTHORS = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Prince", "Eve Davis", "Frank White"]

# Define the metadata fields and their possible values
METADATA_DEFAULTS = {
    "Area Code": "AP7",
    "Area Code Description": "AP7",
    "DCC": "CB",
    "DCC Description": "Approval documents",
    # "Author": "stefan" # Wird jetzt dynamisch aus AUTHORS gewählt
}

# Define a list of possible document types and their DCCs
DOCUMENT_TYPES = [
    {"dcc_code": "MR", "description": "Maintenance Report"},
    {"dcc_code": "INV", "description": "Invoice"},
    {"dcc_code": "TD", "description": "Technical Drawing"},
    {"dcc_code": "QR", "description": "Quality Report"},
    {"dcc_code": "SP", "description": "Spare Parts List"}
]

# Define the pumps and their possible issues for a more realistic dataset
PUMP_ASSETS = ["Pump P-101", "Pump P-102", "Pump P-103"]
MAINTENANCE_ISSUES = [
    "Overheated bearing",
    "Leaking seal",
    "Motor failure",
    "Vibration analysis required",
    "Routine inspection"
]


def generate_document(doc_number):
    """Generates a single document with all required metadata."""

    # Select a random document type
    doc_type = random.choice(DOCUMENT_TYPES)

    # Build the document ID using a counter (will be replaced by API later)
    # doc_id = f"{METADATA_DEFAULTS['Area Code']}-{doc_type['dcc_code']}-{doc_number:05d}" # Entfernt

    # Generate a realistic document title
    if doc_type['dcc_code'] == "MR":
        asset = random.choice(PUMP_ASSETS)
        title = f"Maintenance Report for {asset} - {fake.date_this_year()}"
    elif doc_type['dcc_code'] == "INV":
        title = f"Invoice from {fake.company()} for pump parts"
    elif doc_type['dcc_code'] == "TD":
        asset = random.choice(PUMP_ASSETS)
        title = f"Technical Drawing for {asset}"
    else:
        title = fake.sentence(nb_words=5).replace('.', '')

    # Create the metadata dictionary
    metadata = {
        "Area Code": METADATA_DEFAULTS["Area Code"],
        "Area Code Description": METADATA_DEFAULTS["Area Code Description"],
        "DCC": doc_type["dcc_code"],
        "DCC Description": doc_type["description"],
        "Document Title": title,
        "Author": random.choice(AUTHORS), # Zufälliger Autor
        "Document ID": None # Platzhalter für die später von der API erhaltene ID
    }

    # Add a realistic body/content based on the document type
    content = {}
    if doc_type['dcc_code'] == "MR":
        content = {
            "asset": asset,
            "date": fake.date_between(start_date='-1y', end_date='today').isoformat(),
            "issue": random.choice(MAINTENANCE_ISSUES),
            "actions_taken": fake.paragraph(nb_sentences=3),
            "technician": fake.name(),
            "materials_used": [
                {"part_id": fake.bothify(text='PART-####'), "name": fake.word(), "quantity": random.randint(1, 5)},
                {"part_id": fake.bothify(text='PART-####'), "name": fake.word(), "quantity": random.randint(1, 2)}
            ]
        }
    elif doc_type['dcc_code'] == "INV":
        content = {
            "vendor_name": fake.company(),
            "invoice_date": fake.date_between(start_date='-6m', end_date='today').isoformat(),
            "amount": round(random.uniform(50.0, 5000.0), 2)
        }
    else:
        content = {
            "summary": fake.paragraph(nb_sentences=5),
            "relevant_tags": random.sample(
                ["pump", "motor", "maintenance", "technical", "drawing", "report", "fluid"], k=3
            )
        }

    return {"metadata": metadata, "content": content}


def create_dataset(num_documents, output_dir="pump_house_data", api_endpoint="http://your-api-url/documents"):
    """
    Generates a dataset of documents, sends them to an API,
    and saves them as JSON files (optional, for local copy).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    generated_document_ids = [] # Liste, um generierte IDs zu speichern

    for i in range(1, num_documents + 1):
        doc = generate_document(i) # doc enthält noch keine finale Document ID

        try:
            # Senden Sie das Dokument an Ihre API
            response = requests.post(api_endpoint, json=doc)
            response.raise_for_status() # Löst einen HTTPError für schlechte Antworten (4xx oder 5xx) aus

            api_response_data = response.json()

            external_doc_id = api_response_data.get("document_id") # Annahme: Ihre API gibt die ID als "document_id" zurück

            if external_doc_id:
                doc["metadata"]["Document ID"] = external_doc_id
                generated_document_ids.append(external_doc_id)
                print(f"Document sent to API. Received ID: {external_doc_id}")
            else:
                print(f"Warning: API did not return a document_id for document {i}. Using fallback ID.")
                fallback_id = f"{METADATA_DEFAULTS['Area Code']}-FALLBACK-{i:05d}"
                doc["metadata"]["Document ID"] = fallback_id
                generated_document_ids.append(fallback_id)

        except requests.exceptions.RequestException as e:
            print(f"Error sending document {i} to API: {e}. Using fallback ID.")
            fallback_id = f"{METADATA_DEFAULTS['Area Code']}-ERROR-{i:05d}"
            doc["metadata"]["Document ID"] = fallback_id
            generated_document_ids.append(fallback_id)

        # Optional: Speichern Sie eine lokale Kopie des Dokuments mit der erhaltenen ID
        filename = f"{doc['metadata']['Document ID']}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(doc, f, indent=4)

        print(f"Generated and (optionally) saved document: {filename}")

    return generated_document_ids # Gibt alle generierten IDs zurück


if __name__ == "__main__":
    # Ersetzen Sie dies durch den tatsächlichen Endpunkt Ihrer API
    # Beispiel:
    # generated_ids = create_dataset(num_documents=20, api_endpoint="http://localhost:8000/api/documents")
    # Für lokale Tests ohne API-Endpunkt (wird dann die Fallback-IDs verwenden):
    generated_ids = create_dataset(num_documents=5, api_endpoint="http://localhost:8000/api/documents") # Beispiel mit 5 Dokumenten
    print(f"\nAll generated Document IDs: {generated_ids}")
