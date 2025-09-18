import os
import json
from data_faker import DataFaker
from content_server_document_faker import ContentServerDocumentFaker
from ContentServerApi import ContentServerAPI

def run_generation_process(num_documents: int, output_dir="pump_house_data"):
    """
    Orchestrates the process of generating document data and creating it in the backend.

    Args:
        num_documents: The number of documents to create.
        output_dir: The directory to save a local copy of the generated data.
    """
    # 1. Initialize the components
    data_faker = DataFaker()
    api_client = ContentServerAPI(base_url="http://localhost:8000/api")
    content_server_faker = ContentServerDocumentFaker(api_client=api_client)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    generated_document_ids = []

    print(f"--- Starting document generation for {num_documents} documents ---")
    for i in range(num_documents):
        print(f"\nProcessing document {i + 1}/{num_documents}...")
        
        # 2. Generate document data
        document_data = data_faker.generate_document_data()
        print(f"Generated data for: {document_data['metadata']['Document Title']}")

        # 3. Create document in the backend via API faker
        new_doc_id = content_server_faker.create_document(document_data)

        if new_doc_id:
            # 4. Update data with the ID received from the backend
            document_data["metadata"]["Document ID"] = new_doc_id
            generated_document_ids.append(new_doc_id)
            print(f"Successfully created document with ID: {new_doc_id}")

            # 5. Save a local copy for verification
            filename = f"{new_doc_id}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(document_data, f, indent=4)
            print(f"Saved local copy to: {filepath}")
        else:
            print("Failed to create document in the backend.")

    print(f"\n--- Process finished ---")
    print(f"All generated document IDs: {generated_document_ids}")
    return generated_document_ids

if __name__ == "__main__":
    run_generation_process(num_documents=5)
