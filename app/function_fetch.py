import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.storage.blob import BlobServiceClient
import datetime
import json
import logging
import os
import requests
import time
import traceback
import utilities

fetch_bp = func.Blueprint()

@fetch_bp.function_name(name="CheckForUpdates")
@fetch_bp.schedule(
    schedule="50 22 * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
def check_for_updates(timer):
    # Check if a new version is available
    etag = utilities.get_setting("VersionEtag")
    result = requests.head(utilities.DEPLOYMENT_URL, headers={"If-None-Match": f"{etag}"})
    if result.status_code == 200:
        utilities.copy_url_to_blob()
        # Update etag for future deployments
        etag = result.headers["ETag"]
        utilities.set_setting("VersionEtag", etag)
        logging.info(f"Deployment updated at {str(datetime.datetime.now())}, {etag}")
    elif result.status_code == 304:
        logging.info(f"Version {etag} is up to date")
    else:
        logging.error(f"Error checking for updates: {result.status_code}")

@fetch_bp.function_name(name="FetchCosts")
@fetch_bp.schedule(
    schedule="59 23 * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
def get_costs(timer):
    costmanagement_client = CostManagementClient(credential=DefaultAzureCredential(exclude_environment_credential=True))

    blob_service = BlobServiceClient.from_connection_string(
        conn_str=os.environ["AzureWebJobsStorage"]
    )
    container_client = blob_service.get_container_client("data")
    if not container_client.exists():
        container_client.create_container()
    prices_blob = container_client.get_blob_client("costs.json")

    parameters = {
        "type": "ActualCost",
        "timeframe": "MonthToDate",
        "dataset": {
            "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}},
            "filter": {
                "dimensions": {
                    "name": "ResourceType",
                    "operator": "In",
                    "values": [
                        "microsoft.compute/virtualMachines",
                    ],
                }
            },
            "granularity": "Monthly",
            "grouping": [
                {"type": "Dimension", "name": "ResourceId"},
            ],
        },
    }

    totalCostData = {}

    for subscription in utilities.get_subscriptions():

        try:
            results = costmanagement_client.query.usage(
                scope=f"/subscriptions/{subscription['id']}/", parameters=parameters
            )
        except Exception as e:
            logging.warn(traceback.format_exc())
            logging.warn(f"Error getting cost data for subscription {subscription['id']}")

        for row in results.rows:
            newCostData = {}
            for count, column in enumerate(results.columns):
                newCostData[column.name] = row[count]
            totalCostData[row[2]] = newCostData
        
        # We have a long back-off here to get around rate limits on Cost APIs
        time.sleep(10)
    
    prices_blob.upload_blob(json.dumps(totalCostData), overwrite=True)

    logging.info("Cost info regenerated at %s", str(datetime.datetime.now()))
