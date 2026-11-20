"""CLI entry point"""

import sys
import argparse
import uvicorn
from .spec_loader import SpecLoader
from .app import create_app
from .errors import SpecLoadError


def main(argv=None):
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Mock server for OpenAPI 3 specifications"
    )
    parser.add_argument(
        "spec",
        help="Path to OpenAPI spec file (YAML or JSON)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run server on (default: 8000)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for reproducible mock data generation"
    )

    try:
        args = parser.parse_args(argv)

        # Load spec
        loader = SpecLoader()
        spec = loader.load_spec(args.spec)

        # Create app
        app = create_app(spec, seed=args.seed)

        # Run server
        uvicorn.run(app, host="127.0.0.1", port=args.port)

    except SpecLoadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
