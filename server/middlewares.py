from werkzeug.datastructures import Headers


class CORSMiddleware(object):
    """Add Cross-origin resource sharing headers to every request."""

    def __init__(self, app, origins, paths=None):
        self.app = app
        self.origins = origins
        self.paths = paths or []

    def __call__(self, environ, start_response):
        def add_cors_headers(status, headers, exc_info=None):
            headers = Headers(headers)

            if environ.get("HTTP_ORIGIN") in self.origins and any(
                environ.get("PATH_INFO").startswith(path) for path in self.paths
            ):
                headers.add("Access-Control-Allow-Origin", environ["HTTP_ORIGIN"])

            return start_response(status, headers, exc_info)

        if environ.get("REQUEST_METHOD") == "OPTIONS":
            add_cors_headers("200 Ok", [("Content-Type", "text/plain")])
            return [b"200 Ok"]

        return self.app(environ, add_cors_headers)
