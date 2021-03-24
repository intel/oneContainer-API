"""vertical onecontainer api, cli entrypoint."""

import argparse
import sys

import pytest
import uvicorn

LAUNCH_MODE = "launch"
TEST_MODE = "test"

def cli():
    parser = argparse.ArgumentParser("poetry run oca")
    subparsers = parser.add_subparsers(dest='mode', help=f"Start oneContainer API in a specific mode")
    parser_test = subparsers.add_parser(TEST_MODE)
    parser_test.add_argument(dest='tests', help='List of tests to execute', nargs='*')
    parser_launch = subparsers.add_parser(LAUNCH_MODE)
    args = parser.parse_args()
    if args.mode == LAUNCH_MODE:
        from onecontainer_api.frontend import app
        uvicorn.run(app)
    elif args.mode == TEST_MODE:
        test_args = ["-vv"]
        for test in args.tests:
            test_args.append(f"src/onecontainer_api/{test}")
        pytest.main(test_args)
    else:
        print(f"Unrecognized mode: {args.mode}")
        parser.print_help()
        sys.exit(1)
