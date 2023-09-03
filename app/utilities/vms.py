def set_vm_state(target_state, vm, compute_client):
    """Start or stop a specified VM"""
    resourceGroup = vm.id.split("/")[4]
    vmName = vm.id.split("/")[8]
    if target_state == "started":
        return compute_client.virtual_machines.begin_start(resourceGroup, vmName)
    elif target_state == "stopped":
        return compute_client.virtual_machines.begin_deallocate(resourceGroup, vmName)
    else:
        raise "Invalid VM State"


def extract_vm_state(vm, compute_client):
    """Get the started stopped state of a specified VM"""
    resourceGroup = vm.id.split("/")[4]
    vmName = vm.id.split("/")[8]
    vm_data = compute_client.virtual_machines.get(
        resourceGroup, vmName, expand="instanceView"
    )
    vm_state = None
    for status in vm_data.instance_view.statuses:
        if "PowerState" in status.code:
            vm_state = status.code.replace("PowerState/", "")
    return vm_state
