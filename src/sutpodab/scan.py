import logging
from collections import defaultdict
from enum import Enum
from typing import Tuple, Iterable, Any, Optional, Sequence

import httpx
import faker
from odin.codecs import json_codec
from pyapp.multiprocessing import Pool

from .schema import OpenAPI, Operation, Schema, Method, RequestBody

LOGGER = logging.getLogger(__name__)

fake = faker.Faker()


def read_schema(schema_url: httpx.URL) -> OpenAPI:
    """
    Read the OpenAPI schema from the schema URL and parse into the OpenAPI struct
    """
    response = httpx.get(schema_url)
    return json_codec.load(response, OpenAPI)


def mock_value(schema: Schema):
    """
    Generate a mock value from a type schema
    """
    match schema.type:
        case "string":
            return fake.word()
        case "integer":
            return fake.random_int(min=schema.minimum or 0, max=schema.maximum or 256)
        case _:
            return None


def mock_body(request_body: RequestBody):
    pass


def request_builder(
    schema_url: httpx.URL, path: str, method: Method, operation: Operation
) -> Tuple[Method, httpx.URL, Any]:
    """
    Build a mocked but valid request
    """
    # Generate a valid path
    path_values = {
        param.name: mock_value(param.schema) for param in operation.path_parameters
    }
    request_url = schema_url.copy_with(path=path.format(**path_values))

    # Generate a valid body
    body = None if operation.request_body is None else mock_body(operation.request_body)

    return method, request_url, body


def determine_endpoints(
    schema_url: httpx.URL, api_schema: OpenAPI
) -> Iterable[Tuple[str, httpx.URL]]:
    """
    Parse the API schema to build a list of endpoints
    """

    for path, methods in api_schema.paths.items():
        for method, operation in methods.items():
            if request := request_builder(schema_url, path, method, operation):
                yield request


class Category(Enum):
    Ok = "✅"
    Warning = "😐"
    Error = "🛑"
    Critical = "😬"


Report = Tuple[Category, int, httpx.URL, Optional[str]]


def _categorize(response: httpx.Response) -> Report:
    """
    Categorize the response
    """
    status = response.status_code
    if status == 401:
        return Category.Ok, status, response.url, None
    elif 200 <= status < 300:
        return Category.Critical, status, response.url, response.text
    elif 500 <= status:
        return Category.Error, status, response.url, response.text
    else:
        return Category.Warning, status, response.url, response.text


def _check_endpoint(method: Method, endpoint_url: httpx.URL, body) -> Report:
    """
    Parallel HTTP request
    """
    response = httpx.request(method.value, endpoint_url, data=body)
    return _categorize(response)


def check_endpoints(operations: Iterable[Tuple[str, httpx.URL]]) -> Sequence[Report]:
    """
    Check the end points
    """
    return Pool().starmap(_check_endpoint, operations)


def print_report(results: Sequence[Report]):
    summary = defaultdict(int)

    print("\nResults\n-------\n")
    for category, status, url, text in results:
        summary[category] += 1
        if category is Category.Ok:
            print(f"{category.value}\t{status}\t{url}\n")
        else:
            print(f"{category.value}\t{status}\t{url}\n\t{text}\n")

    print("\nSummary\n-------\n")
    for category in Category:
        print(f"{category.value} {category.name}\t{summary[category]}")
