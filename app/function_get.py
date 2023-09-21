import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.storage.blob import BlobServiceClient
from croniter import croniter
import json
import logging
import os
import requests
import traceback
import utilities

get_bp = func.Blueprint()


@get_bp.function_name(name="Subscriptions")
@get_bp.route(route="api/subscriptions", auth_level=func.AuthLevel.ANONYMOUS)
def get_subscriptions(req: func.HttpRequest) -> func.HttpResponse:
    try:
        return func.HttpResponse(json.dumps(utilities.get_subscriptions()))
    except Exception as ex:
        return func.HttpResponse(str(ex), status_code=500)
    


@get_bp.function_name(name="VMs")
@get_bp.route(route="api/vm", auth_level=func.AuthLevel.ANONYMOUS)
def get_vms(req: func.HttpRequest) -> func.HttpResponse:
    try:
        subscription_id = req.params["id"]

        # Get VM price and cost data from blob storage
        blob_service = BlobServiceClient.from_connection_string(
            conn_str=os.environ["AzureWebJobsStorage"]
        )
        try:
            container_client = blob_service.get_container_client("data")
            # Create the data client if it doesn't already exist
            if not container_client.exists():
                container_client.create_container()
        except:
            return func.HttpResponse(
                "Error connecting to container 'data'", status_code=500
            )

        # prices.json
        # Get currency for display
        currency = utilities.get_setting("Currency")

        # Get current VM cost data
        try:
            costs_blob = container_client.get_blob_client("costs.json")
            costs = json.loads(costs_blob.download_blob().readall())
        except:
            logging.info("Could not read costs.json")
            costs = {}

        logging.info(f"Fetching vms for {subscription_id}")

        compute_client = ComputeManagementClient(
            credential=DefaultAzureCredential(exclude_environment_credential=True), subscription_id=subscription_id
        )

        vms = []

        # NOTE: list_all() appears to have a very long latency on updating the list of VMs, while a
        # list() operation against a resource group name is far quicker
        for vm in compute_client.virtual_machines.list_all():

            monthlyPrice = utilities.get_price(currency, vm)

            # Have to manually trawl the costs because there are case inconsistencies in Azure Resource ids
            actualCost = None
            actualCostCurrency = None
            for costKey in costs.keys():
                if costKey.lower() == vm.id.lower():
                    actualCost = costs[costKey]["Cost"]
                    actualCostCurrency = costs[costKey]["Currency"]

            dateTimeTags = {
                "stopTime": None,
                "startTime": None,
                "daysOfWeek": {
                    "Mon": False,
                    "Tue": False,
                    "Wed": False,
                    "Thu": False,
                    "Fri": False,
                    "Sat": False,
                    "Sun": False,
                },
            }

            # Extract resource group from id
            resourceGroup = vm.id.split("/")[4]

            if vm.tags and utilities.STOPSCHEDULETAG in vm.tags:
                schedule = croniter(vm.tags[utilities.STOPSCHEDULETAG])
                dateTimeTags[
                    "stopTime"
                ] = f"{str(schedule.expanded[1][0]).zfill(2)}:{str(schedule.expanded[0][0]).zfill(2)}"
                for i in range(1, 8, 1):
                    if i in schedule.expanded[4]:
                        dateTimeTags["daysOfWeek"][utilities.daysMapping[i]] = True
                    else:
                        dateTimeTags["daysOfWeek"][utilities.daysMapping[i]] = False
                    # Handling for when days are specified as '*'
                    if "*" in schedule.expanded[4]:
                        dateTimeTags["daysOfWeek"][utilities.daysMapping[i]] = True

            if vm.tags and utilities.STARTSCHEDULETAG in vm.tags:
                schedule = croniter(vm.tags[utilities.STARTSCHEDULETAG])
                dateTimeTags[
                    "startTime"
                ] = f"{str(schedule.expanded[1][0]).zfill(2)}:{str(schedule.expanded[0][0]).zfill(2)}"

            vmData = {
                "id": vm.id,
                "name": vm.name,
                "sku": vm.hardware_profile.vm_size,
                "monthlyCost": monthlyPrice,
                "monthlyCostCurrency": currency,
                "actualCost": actualCost,
                "actualCostCurrency": actualCostCurrency,
                "resourceGroup": resourceGroup
            }

            vmData = {**vmData, **dateTimeTags}

            vms.append(vmData)

        return func.HttpResponse(json.dumps({
            "currency": currency,
            "items" : vms
        }))

    except Exception as ex:
        logging.warn(traceback.format_exc())
        return func.HttpResponse(str(ex), status_code=500)
