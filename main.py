import os
import logging
from app import app
from routes import *

if __name__ == "__main__":
    # Setup logging for debugging
    logging.basicConfig(level=logging.DEBUG)
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
