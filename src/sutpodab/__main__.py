from httpx import URL

from pyapp.app import CliApplication


app = CliApplication(version="0.1")


@app.command
def scan(schema_url: URL):
    """
    Scan an OpenAPI schema and report all endpoints
    """
    from sutpodab.workflows import analyse_openapi

    analyse_openapi.execute(schema_url=schema_url)


if __name__ == "__main__":
    app.dispatch()
