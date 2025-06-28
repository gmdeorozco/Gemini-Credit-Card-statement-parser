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