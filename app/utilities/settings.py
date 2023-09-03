import os

from azure.core.exceptions import ResourceExistsError
from azure.data.tables import TableServiceClient

table_service = TableServiceClient.from_connection_string(
    conn_str=os.environ["AzureWebJobsStorage"]
)

table_service.create_table_if_not_exists(table_name="settings")
settings_table_client = table_service.get_table_client(table_name="settings")

def set_setting(name, value):
    entity = {"PartitionKey": "Settings", "RowKey": name, "Value": value}
    try:
        settings_table_client.create_entity(entity=entity)
    except ResourceExistsError:
        settings_table_client.update_entity(entity=entity)


def get_setting(name):
    setting_entities = settings_table_client.query_entities(f"RowKey eq '{name}'")
    for entity in setting_entities:
        return entity["Value"]
    return None

# If they don't exist create default settings
if not get_setting("Timezone"):
    set_setting("Timezone", "UTC")
if not get_setting("Currency"):
    set_setting("Currency", "GBP")

# Supported currencies taken from
# https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices
CURRENCIES = {
    "USD": "US dollar",
    "AUD": "Australian dollar",
    "BRL": "Brazilian real",
    "CAD": "Canadian dollar",
    "CHF": "Swiss franc",
    "CNY": "Chinese yuan",
    "DKK": "Danish krone",
    "EUR": "Euro",
    "GBP": "British pound",
    "INR": "Indian rupee",
    "JPY": "Japanese yen",
    "KRW": "Korean won",
    "NOK": "Norwegian krone",
    "NZD": "New Zealand dollar",
    "RUB": "Russian ruble",
    "SEK": "Swedish krona",
    "TWD": "Taiwan dollar",
}