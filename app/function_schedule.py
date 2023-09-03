import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
import json
import logging
import utilities

schedule_bp = func.Blueprint()


def generateCronSchedule(vmData, timeString):
    # Create stop time chunk
    stopScheduleMinHour = (
        f"{vmData[timeString].split(':')[1]} {vmData[timeString].split(':')[0]}"
    )
    # Create days chunk
    daysString = ""
    for i in range(1, 8):
        if vmData["daysOfWeek"][utilities.daysMapping[i]]:
            daysString += f"{i},"
    daysString = daysString.rstrip(daysString[-1])

    stopSchedule = f"{stopScheduleMinHour} * * {daysString}"
    return stopSchedule


@schedule_bp.function_name(name="SetSchedule")
@schedule_bp.route(route="api/schedule", auth_level=func.AuthLevel.ANONYMOUS)
def set_schedule(req: func.HttpRequest) -> func.HttpResponse:

    vmData = json.loads(req.get_body())

    # Extract subscription id and resource group from vm id
    subscriptionId = vmData["id"].split("/")[2]
    resourceGroup = vmData["id"].split("/")[4]
    vmName = vmData["id"].split("/")[8]

    compute_client = ComputeManagementClient(
        credential=DefaultAzureCredential(exclude_environment_credential=True), subscription_id=subscriptionId
    )

    vmInstance = compute_client.virtual_machines.get(
        resource_group_name=resourceGroup, vm_name=vmName
    )

    # Check the method type to see if we're adding or deleting a schedule
    if req.method == "DELETE":
        logging.info("REMOVING SCHEDULE")
        # Calculate updated tags
        tags = {}
        if vmInstance.tags:
            tags = vmInstance.tags
        tags.pop(utilities.STARTSCHEDULETAG, None)
        tags.pop(utilities.STOPSCHEDULETAG, None)
    else:

        tags = {}
        if vmInstance.tags:
            tags = vmInstance.tags

        stopSchedule = generateCronSchedule(vmData, "stopTime")
        tags[utilities.STOPSCHEDULETAG] = stopSchedule

        if vmData["startTime"]:
            startSchedule = generateCronSchedule(vmData, "startTime")
            tags[utilities.STARTSCHEDULETAG] = startSchedule
        else:
            tags.pop(utilities.STARTSCHEDULETAG, None)

    add_tags_event = compute_client.virtual_machines.begin_create_or_update(
        resource_group_name=resourceGroup,
        vm_name=vmName,
        parameters={"location": vmInstance.location, "tags": tags},
        polling_interval=1,
    )

    add_tags_event.wait()

    return func.HttpResponse("OK")
