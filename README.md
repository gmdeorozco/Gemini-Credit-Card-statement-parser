# Credit Card Statement Parser (Gemini API)

## Overview

This project provides a Flask-based backend service designed to parse credit card statements provided as PDF files from Google Cloud Storage (GCS) buckets. It leverages the Google Gemini 2.5 Flash model (via Vertex AI) to extract structured information, including statement details (company, balance, due date, interest rate) and a list of individual transactions.

The service is built to be easily containerized and deployed, making it suitable for event-driven architectures (e.g., triggered by new PDF uploads to a GCS bucket via Google Cloud Eventarc and Cloud Run).

---

## Features

- **PDF Parsing:** Extracts structured data from credit card statement PDFs.
- **Gemini 2.5 Flash:** Utilizes the latest Google Gemini model for advanced understanding and extraction.
- **Structured JSON Output:** Returns extracted data in a predefined, easily consumable JSON format.
- **Google Cloud Storage Integration:** Accepts GCS URIs for PDF input.
- **Containerized:** Includes a `Dockerfile` for easy deployment to platforms like Google Cloud Run.
- **Centralized Logging:** Uses `logger_config.py` for consistent application logging.
- **Environment-based Configuration:** Utilizes `.env` for managing sensitive credentials and environment-specific settings.

---

## Project Structure

```
.
├── .env                     # Environment variables (e.g., GCP project, location)
├── .gitignore               # Git ignore file
├── app.py                   # Main Flask application, defines API routes
├── Dockerfile               # Dockerfile for containerizing the application
├── gemini_json_generator.py # Core logic for interacting with Gemini API
├── logger_config.py         # Configuration for application logging
├── README.md                # This README file
└── requirements.txt         # Python dependencies
```

---

## Prerequisites

Ensure you have the following installed:

1. **Python 3.9+** (Recommended 3.10+)
2. **`pip`**: Python package installer
3. **`gcloud CLI`**: Google Cloud SDK authenticated via:
   ```bash
   gcloud auth application-default login
   ```
4. **Google Cloud Project** with [billing enabled](https://cloud.google.com/billing/docs/how-to/enable-disable)
5. **Enabled APIs**:
   - [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
   - [Cloud Storage API](https://console.cloud.google.com/apis/library/storage.googleapis.com)

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/handle_cc_statements.git
cd handle_cc_statements
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter `protobuf` errors, run:

```bash
pip uninstall protobuf -y
pip install protobuf==5.27.0
pip install google-generativeai google-cloud-storage
pip check
```

### 4. Create a `.env` File

Create a `.env` file in the root directory with:

```dotenv
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI=True
```

---

## Running the Application Locally

### 1. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Start Flask Development Server

```bash
python app.py
```

The server should run on `http://0.0.0.0:8080`.

### 3. Test the API Endpoint

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{ "bucket_address": "gs://your-bucket-name/path/to/your-credit-card-statement.pdf" }' \
     http://localhost:8080/
```

---

## API Endpoint

### `POST /`

Handles event-triggered parsing of credit card statements.

#### Request

```json
{
  "bucket_address": "gs://your-gcs-bucket/path/to/statement.pdf"
}
```

#### Response (Success)

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

#### Response (Error)

```json
{
  "status": "error",
  "message": "Description of the error"
}
```

---

## JSON Schema Reference

```json
{
  "type": "object",
  "properties": {
    "credit_card_company": { "type": "string" },
    "credit_card_last4": { "type": "string" },
    "statement_date": { "type": "string", "format": "date" },
    "due_date": { "type": "string", "format": "date" },
    "statement_balance": { "type": "number" },
    "minimum_payment": { "type": "number" },
    "interest_rate": { "type": "number" },
    "transactions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "transaction_date": { "type": "string", "format": "date" },
          "description": { "type": "string" },
          "amount": { "type": "number" }
        }
      }
    }
  },
  "required": [
    "credit_card_company",
    "credit_card_last4",
    "statement_date",
    "due_date",
    "statement_balance",
    "minimum_payment",
    "interest_rate"
  ]
}
```

---

## Logging

The application uses a centralized logger (`logger_config.py`). Logs are output to stdout, which is automatically captured by Cloud Run and forwarded to Google Cloud Logging.

---

## Deployment to Google Cloud Run

### 1. Build Docker Image

```bash
gcloud builds submit --tag gcr.io/your-gcp-project-id/cc-statement-parser:latest .
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy cc-statement-parser \
  --image gcr.io/your-gcp-project-id/cc-statement-parser:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT="your-gcp-project-id",GOOGLE_CLOUD_LOCATION="us-central1",GOOGLE_GENAI_USE_VERTEXAI="True"
```

> ⚠️ Consider removing `--allow-unauthenticated` for production.

---

## Eventarc Trigger (Optional Automation)

### Create Eventarc Trigger

```bash
gcloud eventarc triggers create gcs-to-cc-parser-trigger \
  --destination-run-service=cc-statement-parser \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=your-pdf-bucket-name" \
  --service-account="your-eventarc-service-account@your-gcp-project-id.iam.gserviceaccount.com"
```

Ensure the service account has permissions to invoke Cloud Run and access GCS.

---

## Contributing

Feel free to contribute! Open issues or submit pull requests for enhancements or bug fixes.

---

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.
