from ContentServerApi import ContentServerAPI

class ContentServerDocumentFaker:
    def __init__(self, api_client: ContentServerAPI):
        """
        Initializes the faker with a ContentServerAPI client.

        Args:
            api_client: An instance of the ContentServerAPI to communicate with the backend.
        """
        self.api_client = api_client

    def create_document(self, document_data: dict) -> str | None:
        """
        Creates a document in the backend using the provided data.

        Args:
            document_data: A dictionary containing the document's metadata and content.

        Returns:
            The document ID from the backend if creation is successful, otherwise None.
        """
        # Ruft die API auf, um das Dokument im System zu erstellen
        document_id = self.api_client.create_document_in_system(document_data)
        return document_id
