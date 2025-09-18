import random
from faker import Faker

class DataFaker:
    """A class to generate fake document data."""

    def __init__(self):
        """Initializes the DataFaker."""
        Faker.seed(42)
        self.fake = Faker()
        self.authors = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Prince", "Eve Davis", "Frank White"]
        self.metadata_defaults = {
            "Area Code": "AP7",
            "Area Code Description": "AP7",
            "DCC": "CB",
            "DCC Description": "Approval documents",
        }
        self.document_types = [
            {"dcc_code": "MR", "description": "Maintenance Report"},
            {"dcc_code": "INV", "description": "Invoice"},
            {"dcc_code": "TD", "description": "Technical Drawing"},
            {"dcc_code": "QR", "description": "Quality Report"},
            {"dcc_code": "SP", "description": "Spare Parts List"}
        ]
        self.pump_assets = ["Pump P-101", "Pump P-102", "Pump P-103"]
        self.maintenance_issues = [
            "Overheated bearing",
            "Leaking seal",
            "Motor failure",
            "Vibration analysis required",
            "Routine inspection"
        ]

    def generate_document_data(self) -> dict:
        """Generates a single document with all required metadata and content."""
        doc_type = random.choice(self.document_types)

        asset = None
        if doc_type['dcc_code'] in ["MR", "TD"]:
            asset = random.choice(self.pump_assets)

        title = self._generate_title(doc_type, asset)

        metadata = {
            "Area Code": self.metadata_defaults["Area Code"],
            "Area Code Description": self.metadata_defaults["Area Code Description"],
            "DCC": doc_type["dcc_code"],
            "DCC Description": doc_type["description"],
            "Document Title": title,
            "Author": random.choice(self.authors),
            "Document ID": None  # Placeholder
        }

        content = self._generate_content(doc_type, asset)

        return {"metadata": metadata, "content": content}

    def _generate_title(self, doc_type: dict, asset: str | None) -> str:
        """Generates a realistic document title."""
        if doc_type['dcc_code'] == "MR" and asset:
            return f"Maintenance Report for {asset} - {self.fake.date_this_year()}"
        elif doc_type['dcc_code'] == "INV":
            return f"Invoice from {self.fake.company()} for pump parts"
        elif doc_type['dcc_code'] == "TD" and asset:
            return f"Technical Drawing for {asset}"
        else:
            return self.fake.sentence(nb_words=5).replace('.', '')

    def _generate_content(self, doc_type: dict, asset: str | None) -> dict:
        """Generates a realistic body/content based on the document type."""
        if doc_type['dcc_code'] == "MR" and asset:
            return {
                "asset": asset,
                "date": self.fake.date_between(start_date='-1y', end_date='today').isoformat(),
                "issue": random.choice(self.maintenance_issues),
                "actions_taken": self.fake.paragraph(nb_sentences=3),
                "technician": self.fake.name(),
                "materials_used": [
                    {"part_id": self.fake.bothify(text='PART-####'), "name": self.fake.word(), "quantity": random.randint(1, 5)},
                    {"part_id": self.fake.bothify(text='PART-####'), "name": self.fake.word(), "quantity": random.randint(1, 2)}
                ]
            }
        elif doc_type['dcc_code'] == "INV":
            return {
                "vendor_name": self.fake.company(),
                "invoice_date": self.fake.date_between(start_date='-6m', end_date='today').isoformat(),
                "amount": round(random.uniform(50.0, 5000.0), 2)
            }
        else:
            return {
                "summary": self.fake.paragraph(nb_sentences=5),
                "relevant_tags": random.sample(
                    ["pump", "motor", "maintenance", "technical", "drawing", "report", "fluid"], k=3
                )
            }
