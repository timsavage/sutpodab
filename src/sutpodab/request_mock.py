from typing import Dict, Any

import faker

from .schema import Schema, RequestBody, OpenAPI, Ref

fake = faker.Faker()


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


JSON_CONTENT_TYPE = "application/json"


def resolve_schema(schema: Dict[str, Any], api_schema: OpenAPI):
    """
    Resolve Schema from schema map
    """
    # Check for a ref
    ref = schema.get("$ref")
    if ref:
        ref = Ref(ref)
        return ref.resolve(api_schema)

    for key in ("allOf", "oneOf", "anyOf", "not", "items"):
        data = schema.get(key)
        if data:
            return resolve_schema(data[0], api_schema)

    # return Schema(**schema)


def mock_json_body(media_type: Dict[str, Any], api_schema: OpenAPI):
    # Use a string example if available
    if "example" in media_type:
        example = media_type["example"]
        if isinstance(example, str):
            return example

    if "schema" in media_type:
        schema = resolve_schema(media_type["schema"], api_schema)
        print(schema)


def mock_body(request_body: RequestBody, api_schema: OpenAPI):
    """
    Mock the content body
    """
    if JSON_CONTENT_TYPE in request_body.content:
        return mock_json_body(request_body.content[JSON_CONTENT_TYPE], api_schema)
