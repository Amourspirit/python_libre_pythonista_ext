from __future__ import annotations
import sys
from pathlib import Path
from chart_2_views import Chart2View, ChartKind
from ooodev.utils.file_io import FileIO
import argparse


def args_add(parser: argparse.ArgumentParser) -> None:
    # usage for default start.py -k
    parser.add_argument(
        "-k",
        "--kind",
        const="happy_stock",
        nargs="?",
        dest="kind",
        choices=[e.value for e in ChartKind],
        help="Kind of chart to display (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--soffice",
        dest="soffice",
        default=None,
        help="Path to soffice",
    )


# region main()
def main() -> int:
    if len(sys.argv) == 1:
        sys.argv.append("-k")
        # sys.argv.append("scatter")
    # create parser to read terminal input
    parser = argparse.ArgumentParser(description="main")

    # add args to parser
    args_add(parser=parser)

    # read the current command line args
    # if len(sys.argv) == 1:
    #     parser.print_help()
    #     return 0
    args = parser.parse_args()

    fnm = Path("Documents/Examples/Calc/chartsData.ods")
    p = FileIO.get_absolute_path(fnm)
    if not p.exists():
        fnm = Path("../../../Documents/Examples/Calc/chartsData.ods")
        p = FileIO.get_absolute_path(fnm)
    if not p.exists():
        raise FileNotFoundError("Unable to find path to chartsData.ods")

    kind = ChartKind(args.kind)

    cv = Chart2View(data_fnm=fnm, chart_kind=kind, soffice=args.soffice)
    cv.main()
    return 0


# endregion main()

if __name__ == "__main__":
    SystemExit(main())
