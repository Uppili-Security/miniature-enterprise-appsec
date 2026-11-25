
import argparse
import json
import sys
from pathlib import Path


BLOCKING_SEVERITIES = {"Critical", "High"}


def evaluate_quality_gate(report_path):

    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)

    findings = report.get("findings", [])
    scanners = report.get("scanners", [])

    blocking_findings = [
        finding
        for finding in findings
        if finding.get("severity") in BLOCKING_SEVERITIES
    ]

    failed_scanners = [
        scanner
        for scanner in scanners
        if scanner.get("status") == "failed"
    ]

    missing_scanners = [
        scanner
        for scanner in scanners
        if scanner.get("status") == "not_executed"
    ]

    print("\n===================================")
    print("       SECURITY QUALITY GATE")
    print("===================================")

    print(f"Total findings: {len(findings)}")
    print(f"Blocking findings: {len(blocking_findings)}")

    print("\nBlocking findings:")

    if blocking_findings:
        for finding in blocking_findings:
            print(
                f"- [{finding.get('severity')}] "
                f"{finding.get('scanner')} | "
                f"{finding.get('title')} | "
                f"{finding.get('file')}"
            )
    else:
        print("None")

    print("\nScanner execution status:")

    for scanner in scanners:
        print(
            f"- {scanner.get('scanner')}: "
            f"{scanner.get('status')}"
        )

    print("===================================")

    if failed_scanners or missing_scanners:
        print("QUALITY GATE: FAIL - Incomplete scanner execution")
        return 1

    if blocking_findings:
        print("QUALITY GATE: FAIL - Critical/High findings detected")
        return 1

    print("QUALITY GATE: PASS")
    return 0


def main():

    parser = argparse.ArgumentParser(
        description="Evaluate consolidated AppSec findings"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to parsed-findings.json"
    )

    args = parser.parse_args()

    report_path = Path(args.input)

    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        sys.exit(1)

    sys.exit(evaluate_quality_gate(report_path))


if __name__ == "__main__":
    main()
