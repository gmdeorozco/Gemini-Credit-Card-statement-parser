"""
This module implements a Flask application that serves as an event processor.

It listens for POST requests at its root endpoint ('/') containing a JSON payload.
The application expects a 'bucket_address' field within the received JSON.
Upon receiving a valid payload, it uses the 'bucket_address' to retrieve a JSON statement
via the `gemini_json_generator.get_json_from_statement` function.

The module provides robust error handling and logging for incoming requests and
processing failures. It's designed to be deployed in environments like Google Cloud Run,
utilizing the 'PORT' environment variable for server configuration.
"""
import os
import json
from flask import Flask, request, jsonify
from logger_config import logger
from gemini_json_generator import get_json_from_statement



# Flask app instance
app = Flask(__name__)

# Define the root route for handling incoming requests
@app.route('/', methods=['POST'])
def process_event():
    """
    Handles incoming POST requests containing a JSON payload.

    This function expects a JSON object in the request body. It attempts to extract
    a 'bucket_address' from this payload. If successful, it then calls
    `get_json_from_statement` with the 'bucket_address' to retrieve a JSON statement.
    The function logs the received payload and any errors encountered.

    Returns:
        A JSON response indicating the status of the operation and a message.
        If successful, it includes the retrieved JSON statement.
        Returns a 200 status code on success, 400 if no JSON payload is received,
        and 500 if an unexpected error occurs during processing.
    """
    try:
        # Get the JSON payload from the request body
        data = request.get_json()

        if not data:
            logger.warning("No JSON payload received.")
            return jsonify({"status": "error", "message": "No JSON payload received"}), 400

        logger.info(f"Received event payload: {json.dumps(data, indent=2)}")
        logger.info(f"The bucket address is: {data.get('bucket_address')}")

        json_statement = get_json_from_statement(data.get('bucket_address'))

        
        return jsonify({"status": "success", "message": "Event processed successfully", "statement":json_statement}), 200



    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True) 
        return jsonify({"status": "error", "message": str(e)}), 500

# This ensures the Flask development server runs only when the script is executed directly.
if __name__ == '__main__':
    # Cloud Run populates the PORT environment variable.
    port = int(os.environ.get('PORT', 8080))
    # 'host=0.0.0.0' makes the server accessible from outside the container.
    app.run(debug=True, host='0.0.0.0', port=port)