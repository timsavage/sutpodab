# Sutpodab

A fast and simple scanner to check if your OpenAPI endpoints are properly secured!

Uses the following tools:

- [pyApp](https://docs.pyapp.info/)
- [Odin](https://odin.readthedocs.io/)
- [httpx](https://www.python-httpx.org/)
- [Faker](https://faker.readthedocs.io/)
- [Poetry](https://python-poetry.org/) - For install

## Install

1. Clone out this repository
2. Install dependencies with Poetry `poetry install`
3. Enter the poetry environment `poetry shell`
4. Run the application from the src folder `python3 -m sutpodab scan https://hostname/path/to/your/openapi.json`

