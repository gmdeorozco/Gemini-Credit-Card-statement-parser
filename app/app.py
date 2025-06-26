# app.py

# Import the Flask class from the flask module
from flask import Flask

# Create an instance of the Flask application
# The __name__ argument is a special Python variable that gets the name of the current module.
# Flask uses this to know where to look for resources like templates and static files.
app = Flask(__name__)

# Define a route for the root URL ('/')
# When a user accesses the root of your application, this function will be executed.
@app.route('/')
def hello_world():
    """
    Returns a simple welcome message when the root URL is accessed.
    """
    # Return a string that will be displayed in the browser
    return 'Welcome to your Cloud Run Flask Application!'

# This ensures that the Flask development server runs only when the script is executed directly
# (i.e., not when imported as a module).
if __name__ == '__main__':
    # Get the port from the environment variable or default to 8080
    # Cloud Run typically sets the PORT environment variable.
    import os
    port = int(os.environ.get('PORT', 8080))
    # Run the Flask application
    # host='0.0.0.0' makes the server accessible externally, which is necessary for Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=port)