import os
import requests
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
UP_API_KEY = os.getenv("UP_API_KEY")
YNAB_ACCOUNT_ID = os.getenv("YNAB_ACCOUNT_ID")

# Check if required variables exist
if not UP_API_KEY:
    print("Error: UP_API_KEY not found in environment variables.")
    exit(1)

if not YNAB_ACCOUNT_ID:
    print("Error: YNAB_ACCOUNT_ID not found in environment variables.")
    print("Please run 04-get_ynab_accounts.py and add your account ID to the .env file.")
    exit(1)

# Set up API endpoint and headers
UP_API_URL = "https://api.up.com.au/api/v1"
headers = {
    "Authorization": f"Bearer {UP_API_KEY}",
    "Content-Type": "application/json"
}

# Calculate date 30 days ago
thirty_days_ago = datetime.now() - relativedelta(days=30)
since_date = thirty_days_ago.isoformat()


# Function to get transactions
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


# Function to transform transactions to YNAB format
def transform_to_ynab_format(up_transactions):
    ynab_transactions = []

    for tx in up_transactions:
        # Skip transactions that aren't SETTLED
        if tx["attributes"]["status"] != "SETTLED":
            continue

        # Get transaction date
        date = parser.parse(tx["attributes"]["createdAt"]).strftime("%Y-%m-%d")

        # Get transaction amount (convert from dollars to milliunits)
        amount_in_dollars = float(tx["attributes"]["amount"]["value"])
        # YNAB uses milliunits (1/1000 of currency unit)
        amount_in_milliunits = int(amount_in_dollars * 1000)

        # Get transaction description/payee
        description = tx["attributes"]["description"]

        # Get transaction ID (important for avoiding duplicates)
        import_id = tx["id"][:36]  # YNAB import_id must be <= 36 chars

        ynab_transaction = {
            "account_id": YNAB_ACCOUNT_ID,
            "date": date,
            "amount": amount_in_milliunits,
            "payee_name": description,
            "memo": f"Up Bank: {tx['attributes'].get('rawText', '')}",
            "cleared": "cleared",
            "approved": False,
            "import_id": import_id
        }

        ynab_transactions.append(ynab_transaction)

    return ynab_transactions


# Get transactions
up_transactions = get_transactions(since_date)
print(f"Found {len(up_transactions)} transactions from Up Bank.")

# Transform to YNAB format
ynab_transactions = transform_to_ynab_format(up_transactions)
print(f"Transformed {len(ynab_transactions)} transactions to YNAB format.")

# Print a few sample transformations
print("\nSample transformations:")
for i, (up_tx, ynab_tx) in enumerate(zip(up_transactions[:3], ynab_transactions[:3]), 1):
    print(f"\nTransaction {i}:")
    print("Up Bank format:")
    print(f"  Description: {up_tx['attributes']['description']}")
    print(f"  Amount: {up_tx['attributes']['amount']['value']}")
    print(f"  Date: {up_tx['attributes']['createdAt']}")

    print("YNAB format:")
    print(f"  Payee: {ynab_tx['payee_name']}")
    print(f"  Amount: {ynab_tx['amount']} milliunits ({float(ynab_tx['amount']) / 1000:.2f})")
    print(f"  Date: {ynab_tx['date']}")
    print(f"  Import ID: {ynab_tx['import_id']}")