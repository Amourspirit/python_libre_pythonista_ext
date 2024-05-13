#!/usr/bin/env python
from __future__ import annotations
import sys
import argparse
from src.build import Build
from src.build_args import BuildArgs


# region Args Parse
# region    create parser
def _create_parser(name: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=name)


# endregion create parser
# region    commands
def _args_process_cmd(args: argparse.Namespace) -> None:
    if args.command == "build":
        _args_action_build(args=args)


# endregion commands
def _args_action_build(args: argparse.Namespace) -> None:
    builder = Build(
        args=BuildArgs(
            clean=args.clean,
            oxt_src=args.oxt_source,
            process_tokens=args.process_tokens,
            make_dist=args.make_dist,
            pre_install_pure_packages=args.process_pure,
        )
    )
    print("Processing...", end="", flush=True)
    builder.build()
    print("Done!")


def _args_add_sub_build(parser: argparse.ArgumentParser) -> None:
    build_args = BuildArgs()
    parser.add_argument(
        "-o",
        "--oxt-src",
        help=f"oxt source directory name. Default: {build_args.oxt_src}",
        action="store_true",
        dest="oxt_source",
        default=build_args.oxt_src,
    )
    parser.add_argument(
        "-c", "--no-clean", help="Do not clean build folder", action="store_false", dest="clean", default=True
    )
    parser.add_argument(
        "-t",
        "--no-token-process",
        help="Do not process tokens",
        action="store_false",
        dest="process_tokens",
        default=True,
    )
    parser.add_argument(
        "-p",
        "--no-pure-packages",
        help="Do not pre-install pure packages",
        action="store_false",
        dest="process_pure",
        default=True,
    )
    parser.add_argument(
        "-d", "--no-dist", help="Do not process dist", action="store_false", dest="make_dist", default=True
    )


# endregion Args Parse


# region Main
def _main() -> int:
    # for debugging
    sys.argv.extend(["build"])
    return main()


def main() -> int:
    """The main function."""
    parser = _create_parser("main")
    subparser = parser.add_subparsers(dest="command")
    build_subparser = subparser.add_parser(
        name="build", help=f"Builds the project. Default: clean={BuildArgs.clean}, oxt_src={BuildArgs.oxt_src}"
    )

    _args_add_sub_build(parser=build_subparser)

    # region Read Args
    args = parser.parse_args()
    # endregion Read Args
    # print(args)
    # return 0

    _args_process_cmd(args=args)
    return 0


# endregion Main


if __name__ == "__main__":
    # _touch()
    raise SystemExit(main())
