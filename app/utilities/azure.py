from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient


def get_subscriptions():

    subscription_client = SubscriptionClient(credential=DefaultAzureCredential(exclude_environment_credential=True))

    subscriptions = []
    for subscription in subscription_client.subscriptions.list():
        subscriptions.append(
            {"id": subscription.subscription_id, "name": subscription.display_name}
        )

    return subscriptions
