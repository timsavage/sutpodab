import pyapp_flow as flow
from pyapp_flow.parallel_nodes import MapNode

from . import steps


analyse_openapi = flow.Workflow(
    name="Analyse OpenAPI",
    description="""
    Analyse an OpenAPI and check for authentication
    """,
).nodes(
    steps.fetch_and_parse_schema,
    steps.determine_requests,
    (
        MapNode("api_request", in_var="api_requests")
        .loop(f"{steps.__name__}:process_request")
        .merge_vars("api_results")
    ),
    steps.print_report,
)
