"""
This module provides functionality to parse credit card statements from PDF files
using the Google Gemini API.

It defines a schema for extracting credit card statement details and transactions
and includes a function to process a PDF statement from a GCS bucket,
returning the parsed information as JSON.
"""
import json
import os
from google import genai
from google.genai.types import HttpOptions, Part
from dotenv import load_dotenv

load_dotenv()

statement_response_schema = {
    "type": "object",
    "properties": {
        "credit_card_company": {"type": "string"},
        "credit_card_last4": {"type": "string"},
        "statement_date": {"type": "string", "format": "date"},
        "due_date": {"type": "string", "format": "date"},
        "statement_balance": {"type": "number"},
        "minimum_payment": {"type": "number"},
        "interest_rate": {"type": "number"},
        "credits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "credit_date": {"type": "string", "format": "date"},
                    "description": {"type": "string"},
                    "amount": {"type": "number"}
                },
                "required": ["credit_date", "description", "amount"]
            }
        },
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "transaction_date": {"type": "string", "format": "date"},
                    "description": {"type": "string"},
                    "amount": {"type": "number"}
                },
                "required": ["transaction_date", "description", "amount"]
            }
        },
    },
    "required": [
        "credit_card_company",
        "credit_card_last4",
        "statement_date",
        "due_date",
        "statement_balance",
        "minimum_payment",
        "interest_rate",
        "credits",
        "transactions",
        
    ]
}

client = genai.Client(
    http_options=HttpOptions(
        api_version="v1",
    )
)

def get_json_from_statement(statement_bucket:str):
    """
    Parses a credit card statement from a PDF file located in a Google Cloud Storage bucket
    and extracts structured JSON data.

    Args:
        statement_bucket (str): The Google Cloud Storage URI (e.g., "gs://your-bucket/path/to/statement.pdf")
            of the credit card statement PDF file.

    Returns:
        str: A JSON string containing the parsed credit card statement details
             and transactions, adhering to the `statemet_response_schema`.
    """
    pdf_statement = Part.from_uri(
    file_uri=statement_bucket,
    mime_type="application/pdf",)

    prompt = """
    Your job is to parse the credit card statement that is given in pdf format. 
    You need to extract the statement information and also the transactions of it.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents = [pdf_statement,prompt],
        config = {
            "response_mime_type":"application/json",
            "response_schema": statement_response_schema,

        }
        )
    # print(response.text)
    return response.text