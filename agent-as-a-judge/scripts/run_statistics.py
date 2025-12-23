import logging
from pathlib import Path
import argparse
import re

from agent_as_a_judge.module.statistics import DevStatistics


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_number_from_filename(filename: str) -> int:

    match = re.search(r"(\d+)", filename)
    return int(match.group(1)) if match else float("inf")


def main(instance_dir: Path, workspace_dir: Path):

    instance_files = sorted(
        list(instance_dir.glob("*.json")),
        key=lambda f: extract_number_from_filename(f.stem),
    )

    logging.info(f"Total instances found: {len(instance_files)}")
    total_py_files = 0
    total_code_lines = 0
    total_files = 0
    total_non_code_files = 0

    for instance_file in instance_files:
        instance_name = instance_file.stem
        workspace = workspace_dir / instance_name

        dev_statistics = DevStatistics(workspace)
        (
            total_files_in_workspace,
            total_non_code_files_in_workspace,
            py_files_in_workspace,
            lines_in_workspace,
        ) = dev_statistics.calculate_statistics()
        total_py_files += py_files_in_workspace
        total_code_lines += lines_in_workspace
        total_files += total_files_in_workspace
        total_non_code_files += total_non_code_files_in_workspace

    logging.info("\nTotal summary across all workspaces:")
    logging.info(f"Total files: {total_files}")
    logging.info(f"Total non-Python files: {total_non_code_files}")
    logging.info(f"Total Python files: {total_py_files}")
    logging.info(f"Total lines of Python code: {total_code_lines}")
    logging.info(
        f"Avg. lines of Python code per workspace: {total_code_lines / len(instance_files):.2f}"
    )
    logging.info(
        f"Avg. python files per workspace: {total_py_files / len(instance_files):.2f}"
    )
    logging.info(
        f"Avg. total files per workspace: {total_files / len(instance_files):.2f}"
    )


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Run statistics collection for workspaces."
    )
    parser.add_argument(
        "--benchmark_dir",
        type=str,
        required=True,
        help="Base directory for the DevAI benchmark",
    )
    parser.add_argument(
        "--developer_agent", type=str, required=True, help="Name of the developer agent"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    benchmark_dir = Path(args.benchmark_dir)
    developer_agent = args.developer_agent
    instance_dir = benchmark_dir / "devai/instances"
    workspace_dir = benchmark_dir / f"workspaces/{developer_agent}"
    main(instance_dir, workspace_dir)
