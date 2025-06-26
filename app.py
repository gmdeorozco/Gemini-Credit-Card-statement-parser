# app.py

# Import necessary Flask components
from flask import Flask, request, jsonify
import os
import base64
import json
import logging # Import the logging module

# Configure logging
# Get the root logger
logger = logging.getLogger()
# Set the logging level (e.g., INFO, DEBUG, WARNING, ERROR, CRITICAL)
logger.setLevel(logging.INFO)
# Create a console handler to output logs to stderr (where Cloud Run captures them)
handler = logging.StreamHandler()
# Define the format for the log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Set the formatter for the handler
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)

# Create a Flask app instance
app = Flask(__name__)

# Define the root route for handling incoming requests
# Cloud Run typically expects a service to listen for POST requests when triggered by events.
@app.route('/', methods=['POST'])
def handle_storage_event():
    """
    Handles incoming Cloud Storage event notifications.
    When a file is uploaded to a Google Cloud Storage bucket,
    Eventarc sends a POST request with the event payload to this endpoint.
    """
    try:
        # Get the JSON payload from the request body
        # This payload contains information about the Cloud Storage event.
        event_data = request.get_json()

        if not event_data:
            logger.warning("No JSON payload received.")
            return jsonify({"status": "error", "message": "No JSON payload received"}), 400

        logger.info(f"Received event payload: {json.dumps(event_data, indent=2)}")

        # Extract the Pub/Sub message data, which is base64 encoded.
        # Cloud Storage events are often wrapped in a Pub/Sub message when sent via Eventarc.
        if 'message' in event_data and 'data' in event_data['message']:
            pubsub_message_data = event_data['message']['data']
            # Decode the base64 encoded data
            decoded_data = base64.b64decode(pubsub_message_data).decode('utf-8')
            storage_event = json.loads(decoded_data)

            # Extract relevant information from the storage event
            bucket_name = storage_event.get('bucket')
            file_name = storage_event.get('name')
            content_type = storage_event.get('contentType')
            file_size = storage_event.get('size')
            event_type = event_data['message']['attributes'].get('eventType') # Eventarc event type

            logger.info(f"--- Cloud Storage Event Details ---")
            logger.info(f"Event Type: {event_type}")
            logger.info(f"Bucket: {bucket_name}")
            logger.info(f"File Name: {file_name}")
            logger.info(f"Content Type: {content_type}")
            logger.info(f"File Size: {file_size} bytes")
            logger.info(f"---------------------------------")

            # Check if the file is a PDF
            if file_name and file_name.lower().endswith('.pdf') or (content_type and 'application/pdf' in content_type):
                message = f"Successfully processed PDF file: {file_name} from bucket: {bucket_name}"
                logger.info(message)
                # --- Add your PDF processing logic here ---
                # For example, you might download the file using google-cloud-storage library:
                # from google.cloud import storage
                # client = storage.Client()
                # bucket = client.get_bucket(bucket_name)
                # blob = bucket.blob(file_name)
                # blob.download_to_filename(f'/tmp/{file_name}') # Download to /tmp, Cloud Run's writable directory
                # Then process the downloaded PDF.
                # ----------------------------------------
                return jsonify({"status": "success", "message": message}), 200
            else:
                message = f"File {file_name} is not a PDF. Skipping."
                logger.info(message) # Use info for non-PDF files that are intentionally skipped
                return jsonify({"status": "ignored", "message": message}), 200

        else:
            logger.warning("Received event but missing Pub/Sub message data.")
            return jsonify({"status": "error", "message": "Event payload missing Pub/Sub message data"}), 400

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True) # Use exc_info=True to include traceback
        return jsonify({"status": "error", "message": str(e)}), 500

# This ensures the Flask development server runs only when the script is executed directly.
if __name__ == '__main__':
    # Cloud Run populates the PORT environment variable.
    port = int(os.environ.get('PORT', 8080))
    # 'host=0.0.0.0' makes the server accessible from outside the container.
    app.run(debug=True, host='0.0.0.0', port=port)