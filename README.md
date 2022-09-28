# Sutpodab

A fast and simple scanner to check if your OpenAPI endpoints are properly secured!

In light of the leaky situation of a major Australian telco's API, I have put 
together a quick scanning tool for OpenAPI endpoints that checks that all 
operations are using authentication.

Requires Python 3.10+ and [Poetry](https://python-poetry.org/).

Uses the following packages:

- [pyApp](https://docs.pyapp.info/)
- [Odin](https://odin.readthedocs.io/)
- [httpx](https://www.python-httpx.org/)
- [Faker](https://faker.readthedocs.io/)

## Install

1. Clone out this repository
2. Install dependencies with Poetry `poetry install`
3. Enter the poetry environment `poetry shell`
4. Run the application from the src folder `python3 -m sutpodab scan https://hostname/path/to/your/openapi.json`


## Current Limitations

- Mocking does not handle all types in the OpenAPI spec (yet)
- Not as yet mocking the body so will generate a lot of 422 errors if validation fails
- Assumes all endpoints require Auth
