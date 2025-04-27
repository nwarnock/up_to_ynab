import os
import yaml

"""
Testing how to access resources stored in a yaml
Will use to link static account information between Up and YNAB
"""

# Load resources.yaml
with open("resources.yaml", "r") as file:
    resources = yaml.safe_load(file)

accounts = resources['accounts']
# print(accounts)
# print(type(accounts))

# print(accounts[0])

for account in accounts:
    up_name = account['name']
    up_id = account['up']['id']
    ynab_id = account['ynab']['id']
    print(f"Up name: {up_name}; Up ID: {up_id}; YNAB ID: {ynab_id}")

# How can I use it to find a YNAB account id, given an Up account id?
query = accounts[0]['up']['id']
for account in accounts:
    if(account['up']['id'] == query):
        budget_id = account['ynab']['id']
        break

if budget_id:
    print(f"The YNAB id for Up account {query} is: {budget_id}")
else:
    print(f"No matching YNAB account found for Up account {query}")
