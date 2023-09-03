import azure.functions as func
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential
from croniter import croniter
import datetime
import logging
import pytz
import utilities

startstop_bp = func.Blueprint()


@startstop_bp.function_name(name="StartStop")
@startstop_bp.schedule(
    schedule="*/15 * * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
def start_stop_vms(timer):

    # Get the set timezone
    current_timezone = utilities.get_setting("Timezone")
    if not current_timezone:
        # Default to UTC if the user hasn't set a timezone
        current_timezone = "UTC"
    
    current_time = datetime.datetime.now(pytz.timezone(current_timezone))
    logging.info(f"Evaluating start/stop at {current_time}")

    for subscription in utilities.get_subscriptions():

        logging.info(f"Processing subscription: {subscription['id']}")

        compute_client = ComputeManagementClient(
            credential=DefaultAzureCredential(exclude_environment_credential=True), subscription_id=subscription["id"]
        )

        for vm in compute_client.virtual_machines.list_all():
            logging.info(vm.id)

            if vm.tags and utilities.STOPSCHEDULETAG in vm.tags:
                stop_schedule = croniter(vm.tags[utilities.STOPSCHEDULETAG]).expanded
                # Start and stop tag pair behaviour
                if utilities.STARTSCHEDULETAG in vm.tags:
                    start_schedule = croniter(
                        vm.tags[utilities.STARTSCHEDULETAG]
                    ).expanded
                    # Are we in an on-day?
                    if (
                        current_time.weekday() + 1 in start_schedule[4]
                        or start_schedule[4][0] == "*"
                    ):
                        logging.info(f"[{vm.name}]: has on schedule today")
                        # Are we after the start time?
                        # [[0], [9], ['*'], ['*'], ['*']]
                        start_time = datetime.time(
                            start_schedule[1][0], start_schedule[0][0], 0
                        )
                        stop_time = datetime.time(
                            stop_schedule[1][0], stop_schedule[0][0], 0
                        )
                        logging.info(f"[{vm.name}]: start time {start_time}")
                        logging.info(f"[{vm.name}]: stop time  {stop_time}")
                        # Get the current VM state
                        vm_state = utilities.extract_vm_state(vm, compute_client)
                        logging.info(f"[{vm.name}]: {vm_state}")
                        # Check what the target state of the vm should be, current vm states running/deallocating/deallocated
                        if (
                            current_time.time() > start_time
                            and current_time.time() < stop_time
                        ):
                            logging.info(f"[{vm.name}]: VM should be running")
                            if vm_state != "running":
                                utilities.log_vm_event(vm, "starting")
                                logging.info(
                                    f"[{vm.name}]: {utilities.set_vm_state('started', vm, compute_client).wait()}"
                                )
                        else:
                            logging.info(f"[{vm.name}]: VM should be stopped")
                            if vm_state == "running":
                                utilities.log_vm_event(vm, "stopping")
                                logging.info(
                                    f"[{vm.name}]: {utilities.set_vm_state('stopped', vm, compute_client).wait()}"
                                )
                    else:
                        logging.info(f"[{vm.name}]: is not scheduled to be on today")
                # Stop tag only behaviour
                else:
                    stop_schedule = croniter(
                        vm.tags[utilities.STOPSCHEDULETAG]
                    ).expanded
                    # Are we in an on-day?
                    if (
                        current_time.weekday() + 1 in stop_schedule[4]
                        or stop_schedule[4][0] == "*"
                    ):
                        stop_time = datetime.time(
                            stop_schedule[1][0], stop_schedule[0][0], 0
                        )
                        if current_time.time() > stop_time:
                            vm_state = utilities.extract_vm_state(vm, compute_client)
                            if vm_state == "running":
                                logging.warning(
                                    f"[{vm.name}]: {utilities.set_vm_state('stopped', vm, compute_client).wait()}"
                                )
                    else:
                        logging.warning(
                            f"[{vm.name}]: is not scheduled to be stopped today"
                        )
