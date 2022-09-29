import faker

from .schema import Schema, RequestBody

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


def mock_body(request_body: RequestBody):
    pass
