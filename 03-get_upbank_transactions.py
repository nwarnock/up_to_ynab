import os
import requests
import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from datetime import datetime

"""
This currently fetches transaction from one account, identified in .env
- Note, actually it currently fetches transactions from all accounts, not limited to a particular account
It should ultimately get transactions from all accounts sequentially and sync them with YNAB
"""

# Load environment variables
load_dotenv()

# Get API key from environment variables
UP_API_KEY = os.getenv("UP_API_KEY")

# Check if API key exists
if not UP_API_KEY:
    print("Error: UP_API_KEY not found in environment variables.")
    exit(1)

# Set up API endpoint and headers
UP_API_URL = "https://api.up.com.au/api/v1"
headers = {
    "Authorization": f"Bearer {UP_API_KEY}",
    "Content-Type": "application/json"
}

# Calculate date 30 days ago
thirty_days_ago = datetime.now() - relativedelta(days=30)
print(f"Thirty days ago was {thirty_days_ago}")
since_date = thirty_days_ago.isoformat()


# Function to get transactions
"""
TODO: Probably want this to be from the day before the last sync? Assuming transactions have individual IDs to remove 
duplicates
"""

from datetime import datetime


def get_transactions(since_date):
    # Format the date properly for RFC 3339
    # Convert to UTC and add the 'Z' suffix or proper timezone offset
    if isinstance(since_date, datetime):
        formatted_date = since_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        # If it's already a string, make sure it has timezone info
        formatted_date = since_date if 'Z' in since_date or '+' in since_date else f"{since_date}Z"

    transactions = []
    page_url = f"{UP_API_URL}/transactions?filter[since]={formatted_date}"

    while page_url:
        try:
            print(f"Fetching transactions from: {page_url}")
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            transactions.extend(data["data"])

            # Check if there's a next page
            if "links" in data and "next" in data["links"] and data["links"]["next"]:
                page_url = data["links"]["next"]
            else:
                page_url = None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions: {e}")
            return []

    return transactions


# Get transactions
transactions = get_transactions(since_date)

# Print transaction information
print(f"Found {len(transactions)} transactions in the last 30 days:")
for i, tx in enumerate(transactions[:5], 1):  # Print first 5 transactions
    print(f"\nTransaction {i}:")
    print(f"ID: {tx['id']}")
    print(f"Date: {tx['attributes']['createdAt']}")
    print(f"Description: {tx['attributes']['description']}")
    print(f"Amount: {tx['attributes']['amount']['value']} {tx['attributes']['amount']['currencyCode']}")
    print(f"Status: {tx['attributes']['status']}")
    print(f"Account id: {tx['relationships']['account']['data']['id']}")

if len(transactions) > 5:
    print(f"\n... and {len(transactions) - 5} more transactions")