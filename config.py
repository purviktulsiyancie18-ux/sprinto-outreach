import os
from dotenv import load_dotenv

load_dotenv()

OFFLINE = os.getenv("OFFLINE", "1") == "1"
API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = "gemini-2.0-flash"
TEMPERATURE = 0.7

QUALIFY_THRESHOLD = 0.7   # minimum ICP fit to email
MAX_ROUNDS = 2            # extra page fetches the qualifier may ask for
SCRAPE_ATTEMPTS = 3       # total tries per page on transient failures
SCRAPE_BACKOFF = 1.0      # seconds before first retry; doubles each time
TO_ADDRESS = "growth.lead@example.com"  # case rule: all mail goes to the student's own inbox
