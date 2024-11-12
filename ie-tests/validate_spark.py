import os
import re
import tempfile
import zipfile
from argparse import ArgumentParser, Namespace

from prettytable import PrettyTable


def remove_ascii_colors(line):
    """Clean the line from ascii color code."""
    ansi_escape = re.compile(
        r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final bytere
    )
""",
        re.VERBOSE,
    )
    cleaned_line = ansi_escape.sub("", line.strip())
    return cleaned_line


def parse_args() -> Namespace:
    """Parse command line args."""
    parser = ArgumentParser()
    parser.add_argument(
        "-a", "--archive-logs", help="Path to the archive where run logs are stored."
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Read collections of logs
    args = parse_args()

    zip_file_folder = args.archive_logs
    print("Start analyze the logs from the different runs...")
    logs_archives = os.listdir(zip_file_folder)
    log_results = {}
    log_errors = {}
    log_tests = {}
    log_failed = {}
    print(f"Number of runs: {len(logs_archives)}")
    for log_archive in logs_archives:
        # Extract zip file and extract key stats.
        with tempfile.TemporaryDirectory() as tmpdirname:
            print("created temporary directory", tmpdirname)
            with zipfile.ZipFile(f"{zip_file_folder}/{log_archive}", "r") as zip_ref:
                zip_ref.extractall(tmpdirname)
                log_directory = f"{tmpdirname}/logs/"
                log_files = os.listdir(log_directory)
                for log_file in log_files:
                    lines = []

                    if ".out" in log_file:
                        log_results[log_file] = []
                        log_errors[log_file] = []
                        log_tests[log_file] = []
                        log_failed[log_file] = []
                        # here
                        print("log file name: " + log_file)
                        with open(f"{log_directory}/{log_file}", "r") as file:
                            # Read each line in the file
                            for line in file:
                                clean_line = remove_ascii_colors(line.strip())
                                lines.append(clean_line)
                                if "*** FAILED ***" in clean_line:
                                    log_failed[log_file].append(clean_line)

                                if "-" in clean_line:
                                    test_name = clean_line.split("-")[1].strip()
                                    log_tests[log_file].append(test_name)

                                if "Tests:" in clean_line:
                                    if "FAILURE" in clean_line and "-" in clean_line:
                                        log_errors[log_file].append(
                                            clean_line.split("-")[1]
                                        )
                                    items = clean_line.split(",")
                                    succeeded = int(items[0].split(" ")[-1])
                                    failed = int(items[1].split(" ")[-1])
                                    canceled = int(items[2].split(" ")[-1])
                                    ignored = int(items[3].split(" ")[-1])
                                    pending = int(items[4].split(" ")[-1])
                                    r = (succeeded, failed, canceled, ignored, pending)

                                    log_results[log_file].append(r)
                    # write cleanup file for debug purposes.
                    with open(f"/tmp/cleaned_{log_file}", "w") as f:
                        for line in lines:
                            f.write(f"{line}\n")

    table = PrettyTable()
    table.field_names = [
        "Test",
        "Succeeded",
        "Failed",
        "Canceled",
        "Ignored",
        "Pending",
        "Total",
        "Executed test modules",
        "Failed Tests",
    ]

    for file, results in log_results.items():
        succeeded = 0
        failed = 0
        canceled = 0
        ignored = 0
        pending = 0
        for res in results:
            succeeded += res[0]
            failed += res[1]
            canceled += res[2]
            ignored += res[3]
            pending += res[4]
        total = succeeded + failed + canceled + ignored + pending
        table.add_row(
            [
                file,
                succeeded,
                failed,
                canceled,
                ignored,
                pending,
                total,
                len(log_tests[file]),
                len(log_failed[file]),
            ]
        )

    print(table)
    # print failed tests over the runs
    print("\n\n")
    print("Failed tests:")
    for file, _ in log_results.items():
        print(
            "---------------------------------------------------------------------------"
        )
        print(f"Filename: {file}")
        print(f"Number of failed tests: {len(log_failed[file])}")
        print(
            "==========================================================================="
        )
        for failed_test in log_failed[file]:
            print(f"\t {failed_test}")
        print(
            "---------------------------------------------------------------------------"
        )
    print("End of the process.")
