Okay, here is the complete Markdown content for your `README.md` file, ready to copy and paste.

```markdown
# Credit Card Statement Parser (Gemini API)

## Overview

This project provides a Flask-based backend service designed to parse credit card statements provided as PDF files from Google Cloud Storage (GCS) buckets. It leverages the Google Gemini 2.5 Flash model (via Vertex AI) to extract structured information, including statement details (company, balance, due date, interest rate) and a list of individual transactions.

The service is built to be easily containerized and deployed, making it suitable for event-driven architectures (e.g., triggered by new PDF uploads to a GCS bucket via Google Cloud Eventarc and Cloud Run).

## Features

* **PDF Parsing:** Extracts structured data from credit card statement PDFs.
* **Gemini 2.5 Flash:** Utilizes the latest Google Gemini model for advanced understanding and extraction.
* **Structured JSON Output:** Returns extracted data in a predefined, easily consumable JSON format.
* **Google Cloud Storage Integration:** Accepts GCS URIs for PDF input.
* **Containerized:** Includes a `Dockerfile` for easy deployment to platforms like Google Cloud Run.
* **Centralized Logging:** Uses `logger_config.py` for consistent application logging.
* **Environment-based Configuration:** Utilizes `.env` for managing sensitive credentials and environment-specific settings.

## Project Structure

```

.
├── .env                  \# Environment variables (e.g., GCP project, location)
├── .gitignore            \# Git ignore file
├── app.py                \# Main Flask application, defines API routes
├── Dockerfile            \# Dockerfile for containerizing the application
├── gemini\_json\_generator.py \# Core logic for interacting with Gemini API and parsing statements
├── logger\_config.py      \# Configuration for application logging
├── README.md             \# This README file
└── requirements.txt      \# Python dependencies

````

## Prerequisites

Before you begin, ensure you have the following:

1.  **Python 3.9+:** (Recommended 3.10 or higher, compatible with Cloud Shell's Python 3.12)
2.  **`pip`:** Python package installer.
3.  **`gcloud CLI`:** Google Cloud SDK installed and authenticated (`gcloud auth application-default login` if running locally outside Cloud Shell; otherwise, Cloud Shell handles authentication automatically).
4.  **Google Cloud Project:** A GCP project with [billing enabled](https://cloud.google.com/billing/docs/how-to/enable-disable).
5.  **Enabled APIs:**
    * [**Vertex AI API**](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
    * [**Cloud Storage API**](https://console.cloud.google.com/apis/library/storage.googleapis.com)

## Local Development Setup

Follow these steps to get the application running on your local machine or in Google Cloud Shell:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/handle_cc_statements.git](https://github.com/your-username/handle_cc_statements.git) # Replace with your repo URL
    cd handle_cc_statements
    ```

2.  **Create and Activate a Python Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    * **Important Note on `protobuf`:** If you encounter `TypeError: pop expected at most 1 argument, got 2` or dependency conflicts related to `protobuf` (e.g., `grpcio-status` or `google-ai-generativelanguage` requiring `protobuf < 6.0dev`), you might need to manually manage your `protobuf` version. A common fix is:
        ```bash
        pip uninstall protobuf -y
        pip install protobuf==5.27.0 # Or another 5.x.x version compatible with your other libraries
        pip install google-generativeai google-cloud-storage # Reinstall to ensure compatibility
        ```
        Then, run `pip check` to verify no conflicts.

4.  **Create a `.env` file:**
    Create a file named `.env` in the root directory of your project (`handle_cc_statements/`). Add the following content, replacing the placeholder values with your actual GCP project ID and desired Vertex AI location.

    ```dotenv
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="us-central1" # Example: 'us-central1', 'us-east1', 'europe-west1' etc.
    GOOGLE_GENAI_USE_VERTEXAI=True
    ```
    * **`GOOGLE_CLOUD_PROJECT`**: Your Google Cloud Project ID where the Vertex AI API is enabled.
    * **`GOOGLE_CLOUD_LOCATION`**: The Google Cloud region where you want to access the Gemini model (e.g., `us-central1`). Ensure the model you intend to use (`gemini-2.5-flash`) is available in this region.
    * **`GOOGLE_GENAI_USE_VERTEXAI`**: Set to `True` to explicitly route requests through the Vertex AI endpoint.

## Running the Application Locally (for Testing)

1.  **Ensure your virtual environment is active.**
    ```bash
    source .venv/bin/activate
    ```

2.  **Start the Flask development server:**
    ```bash
    python app.py
    ```
    You should see output indicating the server is running on `http://0.0.0.0:8080`.

3.  **Test the API Endpoint:**
    Open a new terminal (if in Cloud Shell, use `File > New Terminal`).
    You can use `curl` to send a `POST` request to your running application.

    ```bash
    curl -X POST \
         -H "Content-Type: application/json" \
         -d '{ "bucket_address": "gs://your-bucket-name/path/to/your-credit-card-statement.pdf" }' \
         http://localhost:8080/
    ```
    * Replace `your-bucket-name/path/to/your-credit-card-statement.pdf` with an actual GCS URI to a PDF statement you've uploaded.
    * If running in Google Cloud Shell, use the "Web Preview" button (eye icon) in the top bar, select "Change Port" and enter `8080`. Then use `curl` from a *separate* Cloud Shell terminal.

    The application will log processing steps in the terminal where `app.py` is running, and the `curl` command will display the JSON response.

## API Endpoint

The application exposes a single `POST` endpoint:

### `POST /`

Handles incoming requests, typically from Cloud Storage event notifications.

* **Request Method:** `POST`
* **Content-Type:** `application/json`
* **Request Body Example:**
    ```json
    {
      "bucket_address": "gs://your-gcs-bucket/path/to/statement.pdf"
    }
    ```
* **Response (Success):**
    ```json
    {
      "status": "success",
      "message": "Event processed successfully",
      "statement": {
        "credit_card_company": "Example Bank",
        "credit_card_last4": "1234",
        "statement_date": "2025-06-15",
        "due_date": "2025-07-10",
        "statement_balance": 1234.56,
        "minimum_payment": 50.00,
        "interest_rate": 0.1899,
        "transactions": [
          {
            "transaction_date": "2025-06-01",
            "description": "Grocery Store",
            "amount": 75.20
          },
          {
            "transaction_date": "2025-06-03",
            "description": "Online Shopping",
            "amount": 120.50
          }
        ]
      }
    }
    ```
* **Response (Error):**
    ```json
    {
      "status": "error",
      "message": "Description of the error"
    }
    ```

## JSON Schema Reference

The `statement` object returned in the successful response adheres to the following JSON schema:

```json
{
    "type": "object",
    "properties": {
        "credit_card_company": {"type": "string"},
        "credit_card_last4": {"type": "string"},
        "statement_date" : {"type": "string", "format": "date"},
        "due_date" : {"type": "string", "format": "date"},
        "statement_balance" : {"type": "number"},
        "minimum_payment" : {"type": "number"},
        "interest_rate" : {"type": "number"},
        "transactions" : {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "transaction_date" : {"type": "string", "format": "date"},
                    "description" : {"type": "string"},
                    "amount" : {"type": "number"}
                }
            }
        }
    },
    "required": ["credit_card_company", "credit_card_last4", "statement_date", "due_date", "statement_balance", "minimum_payment", "interest_rate"]
}
````

## Logging

The application uses a centralized logger configured in `logger_config.py`. Logs are output to the standard output (stdout), which is automatically captured by Cloud Run and sent to Cloud Logging.

## Deployment to Google Cloud Run

This application is designed for containerized deployment, making Google Cloud Run an ideal platform.

1.  **Build the Docker Image:**

    ```bash
    gcloud builds submit --tag gcr.io/your-gcp-project-id/cc-statement-parser:latest .
    ```

    Replace `your-gcp-project-id` with your actual Google Cloud project ID.

2.  **Deploy to Cloud Run:**

    ```bash
    gcloud run deploy cc-statement-parser \
      --image gcr.io/your-gcp-project-id/cc-statement-parser:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars GOOGLE_CLOUD_PROJECT="your-gcp-project-id",GOOGLE_CLOUD_LOCATION="us-central1",GOOGLE_GENAI_USE_VERTEXAI="True"
    ```

      * Replace `your-gcp-project-id` and `us-central1` with your specific values.
      * `--allow-unauthenticated` is used for public access or if you plan to secure it later with Eventarc. For production, consider `no-allow-unauthenticated` and invoke via service accounts.
      * The `--set-env-vars` explicitly passes the necessary configuration to the Cloud Run service.

3.  **Set up an Eventarc Trigger (Optional, but recommended for automation):**
    To automate the parsing when a new PDF is uploaded to GCS:

      * Create a Cloud Storage bucket for your PDF statements.
      * Create an Eventarc trigger that listens for new object finalizations (`google.cloud.storage.object.v1.finalized`) in that bucket.
      * Configure the trigger to send events to your deployed Cloud Run service.

    You can create an Eventarc trigger via the Google Cloud Console or `gcloud CLI`. Here's a simplified `gcloud` example:

    ```bash
    gcloud eventarc triggers create gcs-to-cc-parser-trigger \
      --destination-run-service=cc-statement-parser \
      --destination-run-region=us-central1 \
      --event-filters="type=google.cloud.storage.object.v1.finalized" \
      --event-filters="bucket=your-pdf-bucket-name" \
      --service-account="your-eventarc-service-account@your-gcp-project-id.iam.gserviceaccount.com"
    ```

    Ensure the service account has permissions to invoke Cloud Run and read from your GCS bucket.

## Contributing

Feel free to contribute to this project. Please open issues or pull requests for any improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE.md) - see the `LICENSE.md` file for details (if you have one, otherwise remove this line).

```
```