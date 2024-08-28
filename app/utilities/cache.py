### Cache of looked up prices
import logging
import os
import requests

from datetime import datetime, timedelta
from azure.data.tables import TableServiceClient, UpdateMode

table_service = TableServiceClient.from_connection_string(
    conn_str=os.environ["AzureWebJobsStorage"]
)

table_service.create_table_if_not_exists(table_name="pricecache")
cache_table_client = table_service.get_table_client(table_name="pricecache")

def get_price(currency, vm):
    vm_type = "Linux"
    # Fix for existing issue https://github.com/sg3-141-592/AzStartStop/issues/15
    # windows_configuration doesn't exist on all VMs
    if hasattr(vm.os_profile, 'windows_configuration'):
        if vm.os_profile.windows_configuration:
            vm_type = "Windows"
    
    lookup_string = f"{currency}_{vm.location}_{vm.hardware_profile.vm_size}_{vm_type}"
    # Create datetime comparison string from a week ago
    expiry_datetime = datetime.utcnow() - timedelta(days=7)
    iso_8601_string = expiry_datetime.isoformat(timespec='seconds') + 'Z'
    lookup_entities = cache_table_client.query_entities(f"RowKey eq '{lookup_string}' and Timestamp ge datetime'{iso_8601_string}'")

    for result in lookup_entities:
        return result["MonthlyPrice"]
    
    price_query = f"https://prices.azure.com/api/retail/prices?currencyCode='{currency}'&$filter=serviceName eq 'Virtual Machines'\
                and priceType eq 'Consumption' and armRegionName eq '{vm.location}' and armSkuName eq '{vm.hardware_profile.vm_size}'"
    price_data = requests.get(price_query)
    if price_data.status_code != 200:
        return None
    price_data = price_data.json()

    monthlyPrice = None
    if vm_type == "Windows":
        for result in price_data["Items"]:
            if "Windows" in result["productName"]:
                monthlyPrice = result["retailPrice"]
                break
    else:
        for result in price_data["Items"]:
            if "Windows" not in result["productName"]:
                monthlyPrice = result["retailPrice"]
                break
    
    if monthlyPrice:
        monthlyPrice = monthlyPrice * 30.0 * 24.0
        
        cacheEntry = {
            "PartitionKey": "cached",
            "RowKey": lookup_string,
            "MonthlyPrice": monthlyPrice,
        }

        cache_table_client.upsert_entity(entity=cacheEntry, mode=UpdateMode.REPLACE)

        logging.info(f"Creating price cache entry {lookup_string}")
    
    # For some reason we've not determined yet sometimes the Azure Price API returns empty data
    
    return monthlyPrice
