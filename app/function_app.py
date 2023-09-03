import azure.functions as func
from azure.data.tables import TableServiceClient
import aiofile
import json
import mimetypes
import os
import pathlib

from function_fetch import fetch_bp
from function_get import get_bp
from function_startstop import startstop_bp
from function_schedule import schedule_bp
from function_settings import timezone_bp

app = func.FunctionApp()
app.register_functions(fetch_bp)
app.register_functions(get_bp)
app.register_functions(startstop_bp)
app.register_functions(schedule_bp)
app.register_functions(timezone_bp)


@app.function_name(name="Signup")
@app.route(route="api/signup", auth_level=func.AuthLevel.ANONYMOUS)
def signup(req: func.HttpRequest) -> func.HttpResponse:

    signup_data = json.loads(req.get_body())

    table_service = TableServiceClient.from_connection_string(
        conn_str=os.environ["AzureWebJobsStorage"]
    )
    table_service.create_table_if_not_exists(table_name="signups")
    table_client = table_service.get_table_client(table_name="signups")

    table_client.create_entity(
        entity={"PartitionKey": signup_data["email"], "RowKey": "v0.1"}
    )

    return func.HttpResponse("OK")


# Functions are loaded based on alphabetical order. So updating the name can
# make /api calls take precedence over static files
@app.function_name(name="zGetStaticFile")
@app.route(route="{*filepath}", auth_level=func.AuthLevel.ANONYMOUS)
async def get_static_file(req: func.HttpRequest) -> func.HttpResponse:
    folder = "./dist/"
    filename = req.route_params.get("filepath")
    if "filepath" not in req.route_params:
        filename = "index.html"
    full_path = f"{folder}{filename}"
    response_headers = {
        "Cache-Control": "max-age=3600"
    }
    if pathlib.Path(full_path).exists():
        async with aiofile.async_open(full_path, "rb") as f:
            mimetype = mimetypes.guess_type(filename)
            return func.HttpResponse(
                body=await f.read(), mimetype=mimetype[0], status_code=200, headers=response_headers
            )
    else:
        return func.HttpResponse("Not found", status_code=404)
