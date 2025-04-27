import os
import requests
import yaml
from dotenv import load_dotenv
from datetime import datetime

"""
A function to find the most recent YNAB account reconciliation date, given an Up Bank account ID
# TODO: Store the last known reconciliation date in order to limit transaction history download (if last known exists)
"""

# Load environment variables
load_dotenv()

# Get YNAB API key, budget ID and specific account ID from environment variables
YNAB_API_KEY = os.getenv("YNAB_API_KEY")
YNAB_BUDGET_ID = os.getenv("YNAB_BUDGET_ID")
YNAB_ACCOUNT_ID = os.getenv("YNAB_ACCOUNT_ID")

# Get Up API key, and an account id to use for testing
UP_API_KEY = os.getenv("UP_API_KEY")
UP_DEBITS_ACCOUNT_ID = os.getenv("UP_DEBITS_ACCOUNT_ID")


# Temporarily store specific Up account id here; later will pass from function call to generalise; ie loop over accounts
UP_ACCOUNT_ID = UP_DEBITS_ACCOUNT_ID
# TODO: probably need to make this work for account type as well
# Or maybe if UP_ACCOUNT_ID is not set, then operate on savers accounts


# Check that YNAB API key exists in .env file
if not YNAB_API_KEY:
    print("Error: YNAB_API_KEY not found in environment variables")
    print("Add your YNAB API key to the .env file")
    exit(1)

# Check that YNAB_ACCOUNT_ID exists in .env file
if not YNAB_ACCOUNT_ID:
    print("Error: YNAB_ACCOUNT not found in environment variables")
    print("Add your account ID as YNAB_ACCOUNT_ID in the .env file")
    exit(1)


# Set up YNAB API endpoint and headers
YNAB_API_URL = "https://api.ynab.com/v1"
headers = {
    "Authorization": f"Bearer {YNAB_API_KEY}",
    "Content-Type": "application/json"
}


def find_ynab_account_name_from_id(ynab_account_id):
    """
    Given a YNAB account id, returns its human-readable account name for reporting purposes

    Args:
        ynab_account_id (str)

    Returns:
        str: YNAB account name corresponding to YNAB account ID
    """
    # Make a request to the accounts endpoint
    response = requests.get(
        f"{YNAB_API_URL}/budgets/{YNAB_BUDGET_ID}/accounts/{ynab_account_id}",
        headers=headers)

    # Check if request was successful
    response.raise_for_status()

    # Parse the response to obtain account name
    data = response.json()  # Obviously this returns a json

    return data['data']['account']['name']


current_ynab_account_name = find_ynab_account_name_from_id(YNAB_ACCOUNT_ID)
print(f"Current YNAB account name is: \n  - {current_ynab_account_name}")


# Get transaction info for given account and determine reconciliation date
# TODO: Remove hard-coded date; this was for testing and development only
def determine_ynab_account_reconciliation_date(ynab_account_id):
    try:
        # Make a request to the transactions endpoint
        response = requests.get(f"{YNAB_API_URL}/budgets/{YNAB_BUDGET_ID}/accounts/{ynab_account_id}/transactions?since_date=2025-03-15", headers=headers)

        # Check if request was successful
        response.raise_for_status()
        # print(response.raise_for_status()) # 'None', if successful

        # Print the response
        data = response.json() # Obviously this returns a json
        # print("Successfully connected to YNAB API")
        # print(data)
        # print(data['data'])
        # print(data['data']['transactions']) # Individual transactions contained within {}
        # print(type(data['data']['transactions'])) # list

        # # Look at the first transaction
        # print(data['data']['transactions'][0]) # Print the first transaction
        # print(type(data['data']['transactions'][0])) # dict

        # # Look at elements of this dictionary
        # print(data['data']['transactions'][0]['date'])
        # print(type(data['data']['transactions'][0]['date'])) # str - note that this is not a date

        # transaction_date = data['data']['transactions'][0]['date']
        # print(f"Date of current transaction is: {transaction_date}")

        # transaction_datetime = datetime.strptime(transaction_date, '%Y-%m-%d')
        # print(f"datetime representation of current transaction is: {transaction_datetime}")


        # Print dates of reconciled transactions
        reconciled_dates = []

        for transaction in data['data']['transactions']:
            if transaction['cleared'] == "reconciled":
                transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                # print(f"Date of current transaction is: {transaction_date}")
                # TODO: Should the next line use reconciled_dates.extend()? What does that do?
                reconciled_dates.append(transaction_date)

        # print(reconciled_dates)

        last_reconciled_date = max(reconciled_dates)
        print(f"{current_ynab_account_name} was last reconciled on: {last_reconciled_date}")
        # TODOx Add account name to final print statement

        return last_reconciled_date

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to YNAB API: {e}")

reconciliation_date = determine_ynab_account_reconciliation_date(YNAB_ACCOUNT_ID)
# print(test)



"""
Retrieve all Up transactions from the YNAB reconciliation date to present
"""

# Set up 'Up Bank' API endpoint and headers
UP_API_URL = "https://api.up.com.au/api/v1"
headers = {
    "Authorization": f"Bearer {UP_API_KEY}",
    "Content-Type": "application/json"
}

def get_up_account_transactions(up_account_id, since_date):
    # Format the date properly for RFC 3339
    # Convert to UTC and add the 'Z' suffix or proper timezone offset
    if isinstance(since_date, datetime):
        formatted_date = since_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        # If it's already a string, make sure it has timezone info
        formatted_date = since_date if 'Z' in since_date or '+' in since_date else f"{since_date}Z"

    transactions = []
    page_url = f"{UP_API_URL}/accounts/{up_account_id}/transactions?filter[since]={formatted_date}"

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


# Get Up account transactions
transactions = get_up_account_transactions(UP_ACCOUNT_ID, reconciliation_date)

# Print Up transaction information
print(f"Found {len(transactions)} Up Bank transactions in the last 30 days:")
for i, tx in enumerate(transactions[:5], 1):  # Print first 5 transactions
    print(f"\nTransaction {i}:")
    print(f"ID: {tx['id']}")
    print(f"Date: {tx['attributes']['createdAt']}")
    print(f"Description: {tx['attributes']['description']}")
    print(f"Amount: {tx['attributes']['amount']['value']} {tx['attributes']['amount']['currencyCode']}")
    print(f"Status: {tx['attributes']['status']}")

    if tx['relationships']['transferAccount']['data'] != None:
        print(tx['relationships']['transferAccount']['data']['id'])

    print(f"Account id: {tx['relationships']['account']['data']['id']}") # Current account id

if len(transactions) > 5:
    print(f"\n... and {len(transactions) - 5} more transactions")


"""
Convert Up Bank transactions to YNAB format
"""

ynab_transactions = []

for i, tx in enumerate(transactions):
    # Date
    # date = tx['attributes']['date']
    # Dollar amount
    currency_amount = tx['attributes']['amount']['value']
    # Milliunit amount
    millunit_amount = currency_amount * 1000
    # import id = up bank transaction id
    import_id = tx['id']
    # Set a flag colour; static
    flag_colour = "purple"
    # Payee
    payee_name = tx['attributes']['description'] # eg. 'Transfer from 2Up Spending'
    # Approved; not sure if I'll use this
    approved = False
    # Category name: if this is not set, will YNAB try to auto-categorise?
    # Payee id for transfers only, otherwise payee is payee_name = tx['attributes']['description']
    if "Transfer from" in payee_name:
        payee_id = tx['relationships']['transferAccount']['data']['id'] # Need to look up the YNAB equivalent account from yaml
        print(payee_id)
    # Do these two Up Bank payee ids match for transfers? No, one is human readable text, the other is a hash of some sort
    # How does this transfer look from the other Up Bank account? Can I join them by the transaction id? Ie, not overwrite them


# TODO: Identify transfers to 2up / savers accounts, and assign correctly
"""
"account_name": "Up Dally",
"payee_id": "3de496b6

Note that transfer_account_id DOES match the ynab account id
payee_id for transfers does NOT match the ynab account id

transactions[0]['relationships']['transferAccount']
"""
