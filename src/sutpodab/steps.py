from collections import defaultdict
from typing import Sequence, Any, NamedTuple, Optional

import httpx
import pyapp_flow as flow
from httpx import URL
from odin.codecs import json_codec

from . import request_mock
from .constants import Category
from .schema import OpenAPI, Method, Operation


class APIRequest(NamedTuple):
    """
    Request to be made
    """

    method: str
    url: URL
    data: Optional[Any]
    expect_auth: bool

    def __str__(self):
        return f"{self.method} {self.url}"


class APIResult(NamedTuple):
    """
    Result of request
    """

    request: APIRequest
    category: Category
    status: int
    text: Optional[str]


@flow.step(name="Fetch and parse OpenAPI Schema", output="open_api_schema")
def fetch_and_parse_schema(schema_url: URL) -> OpenAPI:
    """
    Fetch and parse OpenAPI schema
    """
    response = httpx.get(schema_url)
    return json_codec.load(response, OpenAPI)


def _request_builder(
    schema_url: httpx.URL,
    path: str,
    method: Method,
    operation: Operation,
    api_schema: OpenAPI,
) -> APIRequest:
    """
    Scan operation to determine API request
    """
    # Generate a valid path
    path_values = {
        param.name: request_mock.mock_value(param.schema)
        for param in operation.path_parameters
    }
    request_url = schema_url.copy_with(path=path.format(**path_values))

    # Generate a valid body
    data = (
        None
        if operation.request_body is None
        else request_mock.mock_body(operation.request_body, api_schema)
    )

    return APIRequest(method.value, request_url, data, operation.auth_required)


@flow.step(name="Determine requests", output="api_requests")
def determine_requests(
    schema_url: URL, open_api_schema: OpenAPI
) -> Sequence[APIRequest]:
    """
    Process OpenAPI schema and determine a set of requests to be made
    """
    requests = []

    for path, methods in open_api_schema.paths.items():
        requests.extend(
            _request_builder(schema_url, path, method, operation, open_api_schema)
            for method, operation in methods.items()
        )

    return requests


def _analyse_response(api_request: APIRequest, response: httpx.Response) -> APIResult:
    """
    Categorize the response
    """
    status = response.status_code
    if status == 401:
        return APIResult(
            api_request,
            Category.Good,
            status,
            None,
        )
    elif 200 <= status < 300:
        return APIResult(
            api_request,
            Category.Critical,
            status,
            response.text,
        )
    elif 500 <= status:
        return APIResult(
            api_request,
            Category.Error,
            status,
            response.text,
        )
    else:
        return APIResult(
            api_request,
            Category.Warning,
            status,
            response.text,
        )


@flow.step(
    name="Process Request: {api_request.method} {api_request.url}", output="api_results"
)
def process_request(api_request: APIRequest) -> APIResult:
    """
    Make API request and categorise the response
    """
    try:
        response = httpx.request(
            api_request.method, api_request.url, data=api_request.data
        )
    except httpx.TimeoutException as ex:
        return APIResult(api_request, Category.Failed, 0, str(ex))
    return _analyse_response(api_request, response)


@flow.step
def print_report(api_results: Sequence[APIResult]):
    """
    Print the report of the execution
    """
    summary = defaultdict(int)

    print("\nResults\n-------\n")
    for request, category, status, text in api_results:
        summary[category] += 1
        if category is Category.Good:
            print(f"{category.value}\t{status}\t{request}\n")
        else:
            print(f"{category.value}\t{status}\t{request}\n\t{text}\n")

    print("\nSummary\n-------\n")
    for category in Category:
        print(f"{category.value}  {category.name}\t{summary[category]}")

    if summary[Category.Critical] or summary[Category.Error]:
        print("\n👎 Action needed potential missing authentication!")
        return 1
    elif summary[Category.Warning] or summary[Category.Failed]:
        print("\nCould not verify authentication on all operations.")
    else:
        print("\n👍 Looks good!")
