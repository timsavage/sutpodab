from httpx import URL

from pyapp.app import CliApplication


app = CliApplication(version="0.1")


@app.command
def scan(schema_url: URL):
    """
    Scan an OpenAPI schema and report all endpoints
    """
    from sutpodab.scan import (
        read_schema,
        determine_endpoints,
        check_endpoints,
        print_report,
    )

    api_schema = read_schema(schema_url)
    endpoints = determine_endpoints(schema_url, api_schema)
    results = check_endpoints(endpoints)
    return print_report(results)


if __name__ == "__main__":
    app.dispatch()
