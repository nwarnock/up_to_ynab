import os
import requests
from dotenv import load_dotenv

"""
A function to find the most recent YNAB account reconciliation date, given an Up Bank account ID
"""

# Load environment variables
load_dotenv()

# Get YNAB API key, budget ID and specific account ID from environment variables
YNAB_API_KEY = os.getenv("YNAB_API_KEY")
YNAB_BUDGET_ID= os.getenv("YNAB_BUDGET_ID")
YNAB_ACCOUNT_ID = os.getenv("YNAB_ACCOUNT_ID")

# Check if API key exists
if not YNAB_API_KEY:
    print("Error: YNAB_API_KEY not found in environment variables")
    print("Add your YNAB API key to the .env file")
    exit(1)

# Check if YNAB_ACCOUNT_ID exists
if not YNAB_ACCOUNT_ID:
    print("Error: YNAB_ACCOUNT not found in environment variables")
    print("Add your account ID as YNAB_ACCOUNT_ID in the .env file")
    exit(1)

# Set up API endpoint and headers
YNAB_API_URL = "https://api.ynab.com/v1"
headers = {
    "Authorization": f"Bearer {YNAB_API_KEY}",
    "Content-Type": "application/json"
}

# Try to get budget info
try:
    # Make a request to the budgets endpoint
    response = requests.get(f"{YNAB_API_URL}/budgets/{YNAB_BUDGET_ID}/accounts/{YNAB_ACCOUNT_ID}/transactions?since_date=2025-03-15", headers=headers)

    # Check if request was successful
    response.raise_for_status()

    # Print the response
    data = response.json()
    print("Successfully connected to YNAB API")
    print(f"Found  {len(data['data']['transactions'])} transactions:")

    # Print transaction information
    for transaction in data['data']['transactions']:
        print(f"- {transaction['date']}")
        print(f"- {transaction['amount']}")
        print(f"- {transaction['cleared']}")
        if transaction['cleared'] == "reconciled":
            print("Reconciled")
        print()

except requests.exceptions.RequestException as e:
    print(f"Error connecting to YNAB API: {e}")


