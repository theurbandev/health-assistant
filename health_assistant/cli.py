"""Command-line interface for Health Assistant."""

import argparse

from health_assistant import daily_health_tip


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(prog="health_assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("tips", help="print the daily health tip")
    return parser


def main(argv=None) -> int:
    """Run the command-line interface."""
    args = build_parser().parse_args(argv)

    if args.command == "tips":
        print(daily_health_tip())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
