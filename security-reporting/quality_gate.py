import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

BLOCKING_SEVERITIES = {"Critical", "High"}

SEVERITY_RANK = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
    "Informational": 0,
    "Unknown": -1,
}


def deduplicate_findings(findings):
    """Remove exact duplicate findings while preserving order."""
    unique_findings = []
    seen = set()

    for finding in findings:
        fingerprint = (
            finding.get("scanner"),
            finding.get("rule_id"),
            finding.get("title"),
            finding.get("file"),
            finding.get("line"),
            finding.get("package"),
            finding.get("cve"),
        )

        if fingerprint not in seen:
            seen.add(fingerprint)
            unique_findings.append(finding)

    return unique_findings


def get_vulnerability_key(finding):
    """Identify a vulnerability using CVE when available."""
    cve = finding.get("cve")

    if cve:
        return cve

    return (
        finding.get("scanner"),
        finding.get("rule_id"),
        finding.get("title"),
        finding.get("file"),
    )


def get_highest_severity(findings):
    return max(
        findings,
        key=lambda finding: SEVERITY_RANK.get(
            finding.get("severity", "Unknown"), -1
        ),
    ).get("severity", "Unknown")


def evaluate_quality_gate(report_path):

    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)

    findings = report.get("findings", [])
    scanners = report.get("scanners", [])

    unique_findings = deduplicate_findings(findings)

    blocking_findings = [
        finding
        for finding in unique_findings
        if finding.get("severity") in BLOCKING_SEVERITIES
    ]

    # Group blocking findings by CVE or fallback identifier
    vulnerabilities = defaultdict(list)

    for finding in blocking_findings:
        key = get_vulnerability_key(finding)
        vulnerabilities[key].append(finding)

    # Group blocking findings by affected package
    packages = defaultdict(list)

    for finding in blocking_findings:
        package = finding.get("package") or "Unknown package"
        packages[package].append(finding)

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

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print("\n===================================")
    print("       SECURITY QUALITY GATE")
    print("===================================")

    print(f"Original findings: {len(findings)}")
    print(f"Unique findings: {len(unique_findings)}")
    print(f"Duplicates removed: {len(findings) - len(unique_findings)}")
    print(f"Blocking finding records: {len(blocking_findings)}")
    print(f"Unique blocking vulnerabilities: {len(vulnerabilities)}")

    # -----------------------------------------------------
    # PACKAGE SUMMARY
    # -----------------------------------------------------

    print("\nBlocking Vulnerabilities by Package:")
    print("-----------------------------------")

    if packages:

        for package, package_findings in sorted(packages.items()):

            unique_cves = {
                finding.get("cve")
                for finding in package_findings
                if finding.get("cve")
            }

            severity_counts = defaultdict(int)

            for finding in package_findings:
                severity_counts[finding.get("severity", "Unknown")] += 1

            severity_summary = ", ".join(
                f"{severity}: {count}"
                for severity, count in sorted(
                    severity_counts.items(),
                    key=lambda item: SEVERITY_RANK.get(item[0], -1),
                    reverse=True,
                )
            )

            print(
                f"- {package} | "
                f"{len(unique_cves)} unique CVEs | "
                f"{severity_summary}"
            )

    else:
        print("None")

    # -----------------------------------------------------
    # CVE SUMMARY
    # -----------------------------------------------------

    print("\nBlocking Vulnerabilities by CVE:")
    print("-----------------------------------")

    if vulnerabilities:

        for cve, cve_findings in sorted(
            vulnerabilities.items(),
            key=lambda item: str(item[0]),
        ):

            severity = get_highest_severity(cve_findings)

            affected_packages = sorted({
                finding.get("package") or "Unknown package"
                for finding in cve_findings
            })

            scanners_used = sorted({
                finding.get("scanner") or "Unknown scanner"
                for finding in cve_findings
            })

            title = cve_findings[0].get("title", "Unknown vulnerability")

            print(f"\n- {cve}")
            print(f"  Severity: {severity}")
            print(f"  Title: {title}")
            print(f"  Affected packages: {', '.join(affected_packages)}")
            print(f"  Scanners: {', '.join(scanners_used)}")

    else:
        print("None")

    # -----------------------------------------------------
    # SCANNER STATUS
    # -----------------------------------------------------

    print("\nScanner Execution Status:")
    print("-----------------------------------")

    for scanner in scanners:
        print(
            f"- {scanner.get('scanner')}: "
            f"{scanner.get('status')}"
        )

    print("===================================")

    # -----------------------------------------------------
    # QUALITY GATE DECISION
    # -----------------------------------------------------

    if failed_scanners or missing_scanners:

        print("QUALITY GATE: FAIL - Incomplete scanner execution")

        if failed_scanners:
            print("Failed scanners:")
            for scanner in failed_scanners:
                print(f"- {scanner.get('scanner')}")

        if missing_scanners:
            print("Scanners not executed:")
            for scanner in missing_scanners:
                print(f"- {scanner.get('scanner')}")

        return 1

    if blocking_findings:

        print(
            "QUALITY GATE: FAIL - "
            "Critical/High findings detected"
        )

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
        help="Path to parsed-findings.json",
    )

    args = parser.parse_args()

    report_path = Path(args.input)

    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        sys.exit(1)

    sys.exit(evaluate_quality_gate(report_path))


if __name__ == "__main__":
    main()