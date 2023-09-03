import azure.functions as func
import datetime
import json
import pytz
import utilities
from utilities import CURRENCIES

timezone_bp = func.Blueprint()

ALL_TIMEZONES = {}
# Get all timezones and offsets
for timezone in pytz.common_timezones:
    timezone_str = datetime.datetime.now(pytz.timezone(timezone)).strftime("%z")
    ALL_TIMEZONES[timezone] = timezone_str[:3] + ":" + timezone_str[3:]
ALL_TIMEZONES = sorted(ALL_TIMEZONES.items())

@timezone_bp.function_name(name="Currencies")
@timezone_bp.route(route="api/currencies", auth_level=func.AuthLevel.ANONYMOUS)
def get_currencies(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        response = {"currencies": CURRENCIES}
        response["currentCurrency"] = utilities.get_setting("Currency")
        return func.HttpResponse(json.dumps(response, indent=4), status_code=200)
    elif req.method == "POST":
        requestData = json.loads(req.get_body())
        utilities.set_setting("Currency", requestData["Currency"])
        return func.HttpResponse(status_code=204)


@timezone_bp.function_name(name="Timezone")
@timezone_bp.route(route="api/timezone", auth_level=func.AuthLevel.ANONYMOUS)
def get_timezone(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        response = {"timezones": ALL_TIMEZONES}
        response["currentTimezone"] = utilities.get_setting("Timezone")
        return func.HttpResponse(json.dumps(response, indent=4), status_code=200)
    elif req.method == "POST":
        requestData = json.loads(req.get_body())
        utilities.set_setting("Timezone", requestData["Timezone"])
        return func.HttpResponse(status_code=204)
