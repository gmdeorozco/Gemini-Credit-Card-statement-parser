# app.py

# Import necessary Flask components
from flask import Flask, request, jsonify
import os
import base64
import json
from logger_config import logger


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

       # This line is correct for logging the initial raw payload
        logger.info(f"Received event payload: {json.dumps(event_data, indent=2)}")

        # --- Assuming these lines are placed AFTER 'storage_event = json.loads(decoded_data)' ---

        # Corrected: Accessing properties from 'storage_event', not 'event_data'
        logger.info(f"The bucket name is: {event_data.get('bucket')}")
        logger.info(f"The file name is: {event_data.get('name')}")
        logger.info(f"The Content type is: {event_data.get('contentType')}")

        file_address_in_bucket = 'gs://'+event_data.get('bucket')+'/'+event_data.get('name')
        logger.info(f"The file address in the bucket is: {file_address_in_bucket}")
        return jsonify({"status": "success", "message": "Event processed successfully"}), 200

        # ... rest of your code

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True) # Use exc_info=True to include traceback
        return jsonify({"status": "error", "message": str(e)}), 500

# This ensures the Flask development server runs only when the script is executed directly.
if __name__ == '__main__':
    # Cloud Run populates the PORT environment variable.
    port = int(os.environ.get('PORT', 8080))
    # 'host=0.0.0.0' makes the server accessible from outside the container.
    app.run(debug=True, host='0.0.0.0', port=port)