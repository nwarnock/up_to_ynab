import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key and budget ID from environment variables
YNAB_API_KEY = os.getenv("YNAB_API_KEY")
YNAB_BUDGET_ID = os.getenv("YNAB_BUDGET_ID")

# Check if API key and budget ID exist
if not YNAB_API_KEY:
    print("Error: YNAB_API_KEY not found in environment variables.")
    exit(1)

if not YNAB_BUDGET_ID:
    print("Error: YNAB_BUDGET_ID not found in environment variables.")
    print("Please run test_ynab_api.py and add your budget ID to the .env file.")
    exit(1)

# Set up API endpoint and headers
YNAB_API_URL = "https://api.youneedabudget.com/v1"
headers = {
    "Authorization": f"Bearer {YNAB_API_KEY}",
    "Content-Type": "application/json"
}

# Try to get account information
try:
    # Make a request to the accounts endpoint
    response = requests.get(f"{YNAB_API_URL}/budgets/{YNAB_BUDGET_ID}/accounts", headers=headers)

    # Check if request was successful
    response.raise_for_status()

    # Print the response
    data = response.json()
    print("Successfully retrieved accounts from YNAB!")
    print(f"Found {len(data['data']['accounts'])} accounts:")

    # Print account information
    for account in data['data']['accounts']:
        print(f"- {account['name']}")
        print(f"  Account ID: {account['id']}")
        print(f"  Type: {account['type']}")
        print(f"  Balance: {account['balance'] / 1000:.2f}")
        print()

    print("Add your Up Bank account ID from YNAB to the .env file as YNAB_ACCOUNT_ID")

except requests.exceptions.RequestException as e:
    print(f"Error retrieving YNAB accounts: {e}")