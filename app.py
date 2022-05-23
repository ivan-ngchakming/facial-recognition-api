from werkzeug.middleware.profiler import ProfilerMiddleware

from server import app

import argparse

parser = argparse.ArgumentParser(description='Start the Flask development server.')
parser.add_argument('-p', "--profile", action='store_true', help="run the profiler.")
parser.add_argument('-d', "--debug", action='store_true', help="run the server in debug mode.")

args = parser.parse_args()

if args.profile:
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        profile_dir="./logs/profiles"
    )

if __name__ == "__main__":
    app.run(debug=args.debug)
