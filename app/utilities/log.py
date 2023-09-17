### Log VM Start/Stop Activity
import os
import re

from time import time

from azure.data.tables import TableServiceClient

table_service = TableServiceClient.from_connection_string(
    conn_str=os.environ["AzureWebJobsStorage"]
)

table_service.create_table_if_not_exists(table_name="startstoplogs")
logging_table_client = table_service.get_table_client(table_name="startstoplogs")

resourceIdRegex = re.compile(
    "\/subscriptions\/(?P<subscription_id>.+)\/resourceGroups\/(?P<resource_group>.+)\/providers\/(?P<vm_name>.+)",
    flags=re.IGNORECASE,
)


def log_vm_event(vm, event):
    matches = resourceIdRegex.match(vm.id)
    # We have to replace the / in resource names to use them as partition keys
    # Example rowkey
    # f4b4d30b-ebe4-4567-8ffc-54133caa8c59--Microsoft.Compute-virtualMachines-test-vm-2
    logEntry = {
        "PartitionKey": str(time()),
        "RowKey": f'{matches["subscription_id"]}--{matches["vm_name"].replace("/", "-")}',
        "Event": event,
        "ResourceGroup": matches["resource_group"],
    }

    logging_table_client.create_entity(entity=logEntry)


def get_vm_logs(vm_id):
    matches = resourceIdRegex.match(vm_id)
    rowkey = f'{matches["subscription_id"]}--{matches["vm_name"].replace("/", "-")}'
    results = []

    for result in logging_table_client.query_entities(f"RowKey eq '{rowkey}'"):
        results.append({
            "timestamp": str(result._metadata["timestamp"]).split('.')[0],
            "event": result["Event"]
        })
    return results
