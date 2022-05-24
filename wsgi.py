from logging.config import dictConfig

import yaml

from server import app
from server.config import Config

# TODO: Disable file loggers in development environment
dictConfig(yaml.load(open(Config.PROJECT_DIR + "/logging.yaml"), yaml.FullLoader))

if __name__ == "__main__":
    import argparse

    from werkzeug.middleware.profiler import ProfilerMiddleware

    parser = argparse.ArgumentParser(description="Start the Flask development server.")
    parser.add_argument(
        "-p", "--profile", action="store_true", help="run the profiler."
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="run the server in debug mode."
    )

    args = parser.parse_args()

    if args.profile:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir="./logs/profiles")

    app.run(debug=args.debug)
