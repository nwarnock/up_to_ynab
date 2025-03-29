import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
YNAB_API_KEY = os.getenv("YNAB_API_KEY")

# Check if API key exists
if not YNAB_API_KEY:
    print("Error: YNAB_API_KEY not found in environment variables")
    print("Add your YNAB API key to the .env file")
    exit(1)

# Set up API endpoint and headers
YNAB_API_URL = "https://api.youneedabudget.com/v1"
headers = {
    "Authorization": f"Bearer {YNAB_API_KEY}",
    "Content-Type": "application/json"
}

# Try to get budget info
try:
    # Make a request to the budgets endpoint
    response = requests.get(f"{YNAB_API_URL}/budgets", headers=headers)

    # Check if request was successful
    response.raise_for_status()

    # Print the response
    data = response.json()
    print("Successfully connected to YNAB API")
    print(f"Found  {len(data['data']['budgets'])} budgets:")

    # Print budget information
    for budget in data['data']['budgets']:
        print(f"- {budget['name']}")
        print(f"  Budget ID: {budget['id']}")

    # # Prompt to update .env file
    # print("\nPlease add your budget ID to the .env file as YNAB_BUDGET_ID")

except requests.exceptions.RequestException as e:
    print(f"Error connecting to YNAB API: {e}")
