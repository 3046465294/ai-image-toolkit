import sys
import os

# Add project directory to path
project_path = os.path.expanduser('~/ai-image-toolkit')
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Set environment variables (replace with your actual token)
os.environ.setdefault('REPLICATE_API_TOKEN', 'your_replicate_token_here')

# Import Flask app
from app import app as application
