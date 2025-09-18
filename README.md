# DataFaker

This project is a Python script to generate fake document data for a content server. It can be configured to generate various types of documents and can be integrated with a backend API to create the documents in a live system.

## Installation

1.  Clone the repository.
2.  Make sure you have Python and pip installed.
3.  Install the required dependencies from the project root:

    ```sh
    pip install .
    ```

## Usage

To run the data generation process, execute the `main.py` script:

```sh
python main.py
```

This will generate 5 sample documents by default, interact with the (simulated) API, and save local copies in the `pump_house_data` directory.
