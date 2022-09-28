from enum import Enum
from typing import Dict, List, Any

import odin


class Info(odin.Resource):
    """
    The object provides metadata about the API. The metadata MAY be used by
    the clients if needed, and MAY be presented in editing or documentation
    generation tools for convenience.
    """

    title: str = odin.StringField()
    description: str = odin.StringField(null=True)
    terms_of_service: str = odin.UrlField(name="termsOfService", null=True)
    # contact
    # license
    version: str = odin.StringField()


class Server(odin.Resource):
    """
    An object representing a Server.
    """

    url: str = odin.UrlField()
    description: str = odin.StringField(null=True)


class Location(Enum):
    Query = "query"
    Header = "header"
    Path = "path"
    Cookie = "cookie"


class Schema(odin.Resource):
    """
    The Schema Object allows the definition of input and output data types.
    These types can be objects, but also primitives and arrays. This object is
    an extended subset of the JSON Schema Specification Wright Draft 00.
    """

    type: str = odin.StringField()
    format: str = odin.StringField(null=True)
    default: str = odin.StringField(null=True)
    description: str = odin.StringField(null=True)

    title: str = odin.StringField(name="title", null=True)
    multiple_of: str = odin.StringField(name="multipleOf", null=True)
    maximum: str = odin.StringField(name="maximum", null=True)
    exclusive_maximum: str = odin.StringField(name="exclusiveMaximum", null=True)
    minimum: str = odin.StringField(name="minimum", null=True)
    exclusive_minimum: str = odin.StringField(name="exclusiveMinimum", null=True)
    max_length: str = odin.StringField(name="maxLength", null=True)
    min_length: str = odin.StringField(name="minLength", null=True)
    pattern: str = odin.StringField(name="pattern", null=True)
    max_items: str = odin.StringField(name="maxItems", null=True)
    min_items: str = odin.StringField(name="minItems", null=True)
    unique_items: str = odin.StringField(name="uniqueItems", null=True)
    max_properties: str = odin.StringField(name="maxProperties", null=True)
    min_properties: str = odin.StringField(name="minProperties", null=True)
    required: str = odin.StringField(name="required", null=True)
    enum: List[str] = odin.TypedListField(odin.StringField(), null=True)


class Parameter(odin.Resource):
    """
    Describes a single operation parameter.
    """

    name: str = odin.StringField()
    location: Location = odin.EnumField(Location, name="in")
    description: str = odin.StringField(null=True)
    required: bool = odin.BooleanField(default=False, use_default_if_not_provided=True)
    schema: Schema = odin.DictAs(Schema)


class RequestBody(odin.Resource):
    """
    Describes a single request body.
    """

    description: str = odin.StringField(null=True)
    required: bool = odin.BooleanField()
    content = odin.DictField()


class Response(odin.Resource):
    description: str = odin.StringField()


class Operation(odin.Resource):
    """
    Describes a single API operation on a path.
    """

    id: str = odin.StringField(name="operationId", key=True)
    summary: str = odin.StringField()
    description: str = odin.StringField()
    parameters: List[Parameter] = odin.TypedListField(
        odin.DictAs(Parameter),
    )
    request_body: RequestBody = odin.DictAs(
        RequestBody,
        name="requestBody",
        null=True,
    )
    responses: Dict[int, Response] = odin.TypedDictField(
        odin.DictAs(Response),
    )
    tags: List[str] = odin.TypedListField(odin.StringField())
    security: List[Dict[str, Any]] = odin.TypedListField(
        odin.TypedDictField(odin.ListField()),
        null=True,
    )

    @property
    def auth_required(self) -> bool:
        """
        End point requires auth
        """
        return bool(self.security)

    @property
    def path_parameters(self):
        return (
            parameter
            for parameter in self.parameters
            if parameter.location is Location.Path
        )

    @property
    def query_parameters(self):
        return (
            parameter
            for parameter in self.parameters
            if parameter.location is Location.Query
        )


class SecuritySchema(odin.Resource):
    pass


class Components(odin.Resource):
    schemas: Dict[str, Schema] = odin.TypedDictField(
        odin.DictAs(Schema),
        null=True,
    )
    security_schemes: Dict[str, SecuritySchema] = odin.TypedDictField(
        odin.DictAs(SecuritySchema),
        name="securitySchemes",
        null=True,
    )


class Method(str, Enum):
    Options = "options"
    Get = "get"
    Post = "post"
    Put = "put"
    Patch = "patch"
    Delete = "delete"


class OpenAPI(odin.Resource):
    """
    Root OpenAPI specification document

    https://swagger.io/specification/#openapi-object
    """

    schema_version: str = odin.StringField(name="openapi")
    info: Info = odin.DictAs(Info)
    servers: List[Server] = odin.TypedListField(odin.DictAs(Server), null=True)
    paths: Dict[str, Dict[Method, Operation]] = odin.TypedDictField(
        odin.TypedDictField(
            odin.DictAs(Operation),
            key_field=odin.EnumField(Method),
        ),
    )
    components: Components = odin.DictAs(Components)
    # security: List[SecurityRequirement] = odin.TypedListField(odin.DictAs(), null=True)
    tags: List[str] = odin.TypedListField(odin.StringField(), null=True)
