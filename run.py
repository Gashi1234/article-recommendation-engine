import argparse

from app.main import create_app
from app.config.config import Config

app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Defaults come from Config (which can come from env vars)
    parser.add_argument("--host", default=Config.HOST)
    parser.add_argument("--port", type=int, default=Config.PORT)
    parser.add_argument("--debug", action="store_true", default=Config.DEBUG)

    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
