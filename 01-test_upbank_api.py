import os
import requests
from dotenv import load_dotenv

"""
Testing the Up Bank API connection
Also retrieving a list of accounts from which data may be imported
Ultimately I'll want to import data from all accounts
 - accounts outside of "Spending" and "2Up Spending" are savers, and can all be synced to Up Savings in YNAB
    - ie. they act as one accounts
For now, I've only added one account to .env; I'll end up passing them all from a function
Worth noting that this field exists: "accountType":"SAVER" with the alternate being "TRANSACTIONAL"
"""


# Load environment variables
load_dotenv()

# Get API key from environment variables
UP_API_KEY = os.getenv("UP_API_KEY")

# Check if API key exists:
if not UP_API_KEY:
    print("Error: UP_API_KEY not found in environment variables")
    print("Create a .env file containing your Up Bank API key")
    exit(1)

# Set up API endpoint and headers
UP_API_URL = "https://api.up.com.au/api/v1"
headers = {
    "Authorization": f"Bearer {UP_API_KEY}",
    "Content-Type": "application/json"
}

# Try to get account information
try:
    # Make a request to accounts endpoint
    response = requests.get(f"{UP_API_URL}/accounts", headers=headers)

    # Check if the request was successful
    response.raise_for_status()

    # Print the response
    data = response.json()
    print("Connected to Up Bank API")
    print(f"Found {len(data['data'])} accounts:")

    # Print account information
    for account in data['data']:
        print(f"- {account['attributes']['displayName']}: {account['attributes']['balance']['value']} {account['attributes']['balance']['currencyCode']}")
        print(f"    - {account['attributes']['accountType']}: {account['id']}")

except requests.exceptions.RequestException as e:
    print(f"Error connecting to Up Bank API: {e}")
