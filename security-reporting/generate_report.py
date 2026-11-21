
import argparse
import json
import re
from pathlib import Path


# ---------------------------------------------------------
# SCANNER CONFIGURATION
# ---------------------------------------------------------

SCANNERS = [
    {
        "key": "semgrep",
        "name": "Semgrep",
        "type": "SAST",
        "folder": "semgrep-report",
        "format": "sarif"
    },
    {
        "key": "trivy-sca",
        "name": "Trivy SCA",
        "type": "SCA",
        "folder": "trivy-sca-report",
        "format": "sarif"
    },
    {
        "key": "checkov",
        "name": "Checkov",
        "type": "IaC Security",
        "folder": "checkov-report",
        "format": "sarif"
    },
    {
        "key": "owasp-zap",
        "name": "OWASP ZAP",
        "type": "DAST",
        "folder": "owasp-zap-reports",
        "format": "json"
    },
    {
        "key": "gitleaks",
        "name": "Gitleaks",
        "type": "Secrets",
        "folder": "gitleaks-results.sarif",
        "format": "sarif"
    },
    {
        "key": "trivy-container",
        "name": "Trivy Container",
        "type": "Container Security",
        "folder": "trivy-container-report",
        "format": "sarif"
    }
]


# ---------------------------------------------------------
# SEVERITY NORMALIZATION
# ---------------------------------------------------------

def normalize_severity(raw_severity):
    """
    Normalize explicitly supplied security severity values.

    SARIF levels such as error, warning and note are
    deliberately NOT treated as security severity.
    """

    if raw_severity is None:
        return "Unknown"

    severity = str(raw_severity).strip().lower()

    severity_mapping = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "moderate": "Medium",
        "low": "Low",
        "informational": "Informational",
        "info": "Informational",
        "unknown": "Unknown"
    }

    if severity in severity_mapping:
        return severity_mapping[severity]

    # Handle numeric CVSS-style security severity.
    try:
        score = float(severity)

        if score >= 9.0:
            return "Critical"
        elif score >= 7.0:
            return "High"
        elif score >= 4.0:
            return "Medium"
        elif score > 0:
            return "Low"

    except (ValueError, TypeError):
        pass

    return "Unknown"


def extract_severity(properties, rule_properties, result):
    """
    Extract genuine security severity from SARIF metadata.

    Trivy can also embed severity directly in its result
    message, so that is checked as a fallback.
    """

    candidates = [
        properties.get("security-severity"),
        rule_properties.get("security-severity"),
        properties.get("severity"),
        rule_properties.get("severity")
    ]

    for candidate in candidates:
        if candidate is not None:
            return candidate

    # Trivy embeds severity in its SARIF message.
    message = result.get("message", {}).get("text", "")

    match = re.search(
        r"\bSeverity:\s*(CRITICAL|HIGH|MEDIUM|LOW|UNKNOWN)\b",
        message,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return "Unknown"


# ---------------------------------------------------------
# SARIF PARSER
# ---------------------------------------------------------


def parse_sarif(report_path, scanner_name, scanner_type):
    """
    Parse SARIF reports and return normalized findings.
    Supports enriched Trivy vulnerability information.
    """

    findings = []

    with open(report_path, "r", encoding="utf-8-sig") as file:
        sarif_data = json.load(file)

    for run in sarif_data.get("runs", []):

        driver = run.get("tool", {}).get("driver", {})

        rules = {
            rule.get("id"): rule
            for rule in driver.get("rules", [])
            if rule.get("id")
        }

        for result in run.get("results", []):

            rule_id = result.get("ruleId", "Unknown")
            rule = rules.get(rule_id, {})

            properties = result.get("properties") or {}
            rule_properties = rule.get("properties") or {}

            raw_severity = extract_severity(
                properties,
                rule_properties,
                result
            )

            # Preserve SARIF reporting level separately.
            sarif_level = result.get("level", "unknown")

            title = (
                rule.get("shortDescription", {}).get("text")
                or rule.get("name")
                or rule_id
            )

            message = result.get(
                "message", {}
            ).get("text", "No description provided")

            locations = result.get("locations", [])

            file_path = "Unknown"
            line_number = None

            if locations:

                physical_location = (
                    locations[0]
                    .get("physicalLocation", {})
                )

                artifact_location = (
                    physical_location
                    .get("artifactLocation", {})
                )

                region = physical_location.get("region", {})

                file_path = artifact_location.get(
                    "uri", "Unknown"
                )

                line_number = region.get("startLine")

            # Default fields for scanners other than Trivy.
            finding = {
                "scanner": scanner_name,
                "scanner_type": scanner_type,
                "rule_id": rule_id,
                "title": title,
                "severity": normalize_severity(raw_severity),
                "original_severity": raw_severity,
                "sarif_level": sarif_level,
                "message": message,
                "description": message,
                "remediation": (
                    rule.get("help", {}).get("text")
                    or rule.get("help", {}).get("markdown")
                    or "No remediation guidance provided by the scanner."
                ),
                "file": file_path,
                "line": line_number,
                "cve": None,
                "package": None,
                "installed_version": None,
                "fixed_version": None,
                "native_severity": None,
                "security_score": None,
                "advisory_url": None
            }

            # Enrich Trivy findings.
            if scanner_name in ("Trivy Container", "Trivy SCA"):

                trivy = extract_trivy_details(result, rule)

                native_severity = trivy["native_severity"]

                # Prefer Trivy's native severity over its numeric score.
                if native_severity:
                    finding["severity"] = normalize_severity(
                        native_severity
                    )

                finding.update({
                    "original_severity": (
                        native_severity or raw_severity
                    ),
                    "cve": trivy["cve"],
                    "package": trivy["package"],
                    "installed_version": trivy["installed_version"],
                    "fixed_version": trivy["fixed_version"],
                    "native_severity": native_severity,
                    "security_score": trivy["security_score"],
                    "advisory_url": trivy["advisory_url"],
                    "description": trivy["detailed_description"],
                    "remediation": trivy["remediation"]
                })

            findings.append(finding)

    return findings



def extract_trivy_details(result, rule):
    """
    Extract structured vulnerability information from
    Trivy SARIF results.
    """

    import re

    message = result.get("message", {}).get("text", "")

    def extract(pattern):
        match = re.search(
            pattern,
            message,
            re.IGNORECASE | re.MULTILINE
        )

        if match:
            value = match.group(1).strip()
            return value if value else None

        return None

    package = extract(r"^Package:[ \t]*([^\r\n]*)")
    installed_version = extract(
        r"^Installed Version:[ \t]*([^\r\n]*)"
    )
    cve = extract(r"^Vulnerability[ \t]+(\S+)")
    native_severity = extract(
        r"^Severity:[ \t]*([^\r\n]*)"
    )
    fixed_version = extract(
        r"^Fixed Version:[ \t]*([^\r\n]*)"
    )

    link_match = re.search(
        r"^Link:[ \t]*\[[^\]]+\]\((https?://[^)]+)\)",
        message,
        re.IGNORECASE | re.MULTILINE
    )

    advisory_url = (
        link_match.group(1)
        if link_match
        else None
    )

    properties = result.get("properties") or {}
    rule_properties = rule.get("properties") or {}

    score = (
        properties.get("security-severity")
        or rule_properties.get("security-severity")
    )

    if score is not None:
        try:
            score = float(score)
        except (ValueError, TypeError):
            score = None

    # Extract readable vulnerability description.
    description_lines = []

    metadata_pattern = re.compile(
        r"^(Package:|Installed Version:|Vulnerability\s|"
        r"Severity:|Fixed Version:|Link:)",
        re.IGNORECASE
    )

    for line in message.splitlines():

        line = line.strip()

        if not line:
            continue

        if metadata_pattern.match(line):
            continue

        description_lines.append(line)

    detailed_description = (
        " ".join(description_lines)
        or rule.get("fullDescription", {}).get("text")
        or "No detailed description provided."
    )

    if fixed_version:
        remediation = (
            f"Upgrade {package or 'the affected package'} "
            f"from {installed_version or 'the installed version'} "
            f"to fixed version {fixed_version}."
        )
    else:
        remediation = (
            "No fixed version was provided by Trivy. "
            "Review the vendor advisory and package updates "
            "for available remediation."
        )

    return {
        "cve": cve,
        "package": package,
        "installed_version": installed_version,
        "fixed_version": fixed_version,
        "native_severity": native_severity,
        "security_score": score,
        "advisory_url": advisory_url,
        "detailed_description": detailed_description,
        "remediation": remediation
    }

# ---------------------------------------------------------
# OWASP ZAP JSON PARSER
# ---------------------------------------------------------

def parse_zap_json(report_path):
    """
    Parse an OWASP ZAP JSON report.
    """

    findings = []

    with open(report_path, "r", encoding="utf-8-sig") as file:
        zap_data = json.load(file)

    sites = zap_data.get("site", [])

    for site in sites:

        alerts = site.get("alerts", [])

        for alert in alerts:

            raw_severity = (
                alert.get("riskdesc", "Unknown")
                .split(" ")[0]
            )

            severity = normalize_severity(raw_severity)

            instances = alert.get("instances", [])

            # Preserve the alert even if no individual
            # instances are supplied.
            if not instances:
                instances = [{}]

            for instance in instances:

                finding = {
                    "scanner": "OWASP ZAP",
                    "scanner_type": "DAST",
                    "rule_id": alert.get(
                        "pluginId", "Unknown"
                    ),
                    "title": alert.get(
                        "alert", "Unknown alert"
                    ),
                    "severity": severity,
                    "original_severity": raw_severity,
                    "sarif_level": None,
                    "message": alert.get(
                        "desc", "No description provided"
                    ),
                    "description": alert.get(
                        "desc", "No description provided"
                    ),
                    "remediation": alert.get(
                        "solution",
                        "No remediation guidance provided."
                    ),
                    "file": instance.get(
                        "uri", site.get("name", "Unknown")
                    ),
                    "line": instance.get("method")
                }

                findings.append(finding)

    return findings


# ---------------------------------------------------------
# REPORT DISCOVERY
# ---------------------------------------------------------

def discover_scanner_reports(input_dir, scanner):
    """
    Find report files belonging to a configured scanner.
    """

    scanner_dir = input_dir / scanner["folder"]

    if not scanner_dir.exists():
        return []

    if scanner["format"] == "sarif":
        return sorted(scanner_dir.rglob("*.sarif"))

    if scanner["format"] == "json":
        return sorted(scanner_dir.rglob("*.json"))

    return []


# ---------------------------------------------------------
# COLLECT FINDINGS AND SCANNER STATUS
# ---------------------------------------------------------

def collect_findings(input_dir):
    """
    Collect findings from all configured scanners.

    Scanner statuses:
      completed_with_findings
      completed_no_findings
      failed
      not_executed
    """

    all_findings = []
    scanner_status = []

    for scanner in SCANNERS:

        scanner_name = scanner["name"]
        scanner_type = scanner["type"]

        report_files = discover_scanner_reports(
            input_dir,
            scanner
        )

        # No report was found.
        if not report_files:

            scanner_status.append({
                "key": scanner["key"],
                "scanner": scanner_name,
                "scanner_type": scanner_type,
                "status": "not_executed",
                "findings": 0,
                "reports": [],
                "error": None
            })

            continue

        scanner_findings = []
        report_errors = []

        for report_path in report_files:

            try:

                if scanner["format"] == "sarif":

                    parsed = parse_sarif(
                        report_path,
                        scanner_name,
                        scanner_type
                    )

                elif scanner["format"] == "json":

                    parsed = parse_zap_json(report_path)

                else:
                    raise ValueError(
                        "Unsupported report format"
                    )

                scanner_findings.extend(parsed)

            except (
                json.JSONDecodeError,
                OSError,
                KeyError,
                TypeError,
                ValueError
            ) as error:

                report_errors.append({
                    "report": str(report_path),
                    "error": str(error)
                })

        all_findings.extend(scanner_findings)

        # Determine scanner status.
        if report_errors:

            status = "failed"

        elif scanner_findings:

            status = "completed_with_findings"

        else:

            status = "completed_no_findings"

        scanner_status.append({
            "key": scanner["key"],
            "scanner": scanner_name,
            "scanner_type": scanner_type,
            "status": status,
            "findings": len(scanner_findings),
            "reports": [
                str(path.relative_to(input_dir))
                for path in report_files
            ],
            "error": report_errors if report_errors else None
        })

    return all_findings, scanner_status


# ---------------------------------------------------------
# GENERATE CONSOLIDATED JSON REPORT
# ---------------------------------------------------------

def generate_report(input_dir, output_file):

    findings, scanner_status = collect_findings(input_dir)

    report_data = {
        "summary": {
            "total_findings": len(findings),
            "total_scanners": len(SCANNERS),
            "scanners_with_findings": sum(
                1 for scanner in scanner_status
                if scanner["status"] == "completed_with_findings"
            ),
            "scanners_without_findings": sum(
                1 for scanner in scanner_status
                if scanner["status"] == "completed_no_findings"
            ),
            "scanners_failed": sum(
                1 for scanner in scanner_status
                if scanner["status"] == "failed"
            ),
            "scanners_not_executed": sum(
                1 for scanner in scanner_status
                if scanner["status"] == "not_executed"
            )
        },
        "scanners": scanner_status,
        "findings": findings
    }

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return report_data


# ---------------------------------------------------------
# COMMAND LINE ENTRY POINT
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Enterprise Application Security Report Generator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing scanner reports"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output path for consolidated JSON report"
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_file = Path(args.output)

    if not input_dir.exists():

        parser.error(
            f"Input directory does not exist: {input_dir}"
        )

    report_data = generate_report(
        input_dir,
        output_file
    )

    # Display summary.
    print()
    print("===================================")
    print(" ENTERPRISE APPSEC REPORT SUMMARY")
    print("===================================")

    print(
        f"Total findings: "
        f"{report_data['summary']['total_findings']}"
    )

    print(
        f"Total scanners: "
        f"{report_data['summary']['total_scanners']}"
    )

    print("-----------------------------------")

    for scanner in report_data["scanners"]:

        print(
            f"{scanner['scanner']}: "
            f"{scanner['status']} "
            f"({scanner['findings']} findings)"
        )

    print("-----------------------------------")

    print(
        f"Scanners failed: "
        f"{report_data['summary']['scanners_failed']}"
    )

    print(
        f"Scanners not executed: "
        f"{report_data['summary']['scanners_not_executed']}"
    )

    print("===================================")

    print(f"Report saved to: {output_file}")

    print("===================================")


if __name__ == "__main__":
    main()
