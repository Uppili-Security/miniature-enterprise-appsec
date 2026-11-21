
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from html import escape


SEVERITY_ORDER = [
    "Critical",
    "High",
    "Medium",
    "Low",
    "Informational",
    "Unknown"
]


# ---------------------------------------------------------
# LOAD CONSOLIDATED REPORT
# ---------------------------------------------------------

def load_report(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------
# CALCULATE DASHBOARD SUMMARY
# ---------------------------------------------------------

def calculate_summary(data):

    findings = data.get("findings", [])

    severity_counts = {
        severity: 0 for severity in SEVERITY_ORDER
    }

    for finding in findings:

        severity = finding.get("severity", "Unknown")

        if severity not in severity_counts:
            severity = "Unknown"

        severity_counts[severity] += 1

    scanner_counts = {}

    for scanner in data.get("scanners", []):

        scanner_counts[scanner["scanner"]] = scanner.get(
            "findings", 0
        )

    return {
        "total": len(findings),
        "severity": severity_counts,
        "scanners": scanner_counts
    }


# ---------------------------------------------------------
# GENERATE HTML DASHBOARD
# ---------------------------------------------------------

def generate_html(data):

    findings = data.get("findings", [])
    scanners = data.get("scanners", [])

    summary = calculate_summary(data)

    report_generated = datetime.now(
        timezone.utc
    ).strftime("%d %B %Y, %H:%M UTC")

    embedded_data = json.dumps(
        {
            "findings": findings,
            "scanners": scanners,
            "summary": summary
        },
        ensure_ascii=False
    ).replace("</", "<\\/")

    # -----------------------------------------------------
    # SCANNER COVERAGE TABLE
    # -----------------------------------------------------

    scanner_rows = ""

    for scanner in scanners:

        status = scanner.get("status", "unknown")

        scanner_rows += f"""
        <tr>
            <td>{escape(scanner.get("scanner", "Unknown"))}</td>
            <td>{escape(scanner.get("scanner_type", "Unknown"))}</td>
            <td>{scanner.get("findings", 0)}</td>
            <td>
                <span class="status {escape(status)}">
                    {escape(status.replace("_", " ").title())}
                </span>
            </td>
        </tr>
        """

    # -----------------------------------------------------
    # HTML DOCUMENT
    # -----------------------------------------------------

    return f"""<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Enterprise Application Security Dashboard</title>

<style>

/* -------------------------------------------------------
   GLOBAL THEME
------------------------------------------------------- */

:root {{

    --bg: #0b1120;
    --panel: #111b2e;
    --panel-light: #17243a;
    --border: #263650;

    --text: #e5edf8;
    --muted: #91a1b8;

    --accent: #60a5fa;

    --critical: #ef4444;
    --high: #f97316;
    --medium: #eab308;
    --low: #22c55e;
    --info: #38bdf8;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: Inter, Segoe UI, Arial, sans-serif;
}}

.container {{
    max-width: 1500px;
    margin: auto;
    padding: 30px;
}}


/* -------------------------------------------------------
   HEADER
------------------------------------------------------- */

.header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 30px;
}}

.header h1 {{
    margin: 0;
    font-size: 27px;
}}

.header p {{
    color: var(--muted);
    margin-bottom: 0;
}}

.generated {{
    color: var(--muted);
    font-size: 12px;
}}


/* -------------------------------------------------------
   PANELS
------------------------------------------------------- */

.panel {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 22px;
}}

.section-title {{
    font-size: 17px;
    margin: 0 0 18px;
}}


/* -------------------------------------------------------
   EXECUTIVE METRICS
------------------------------------------------------- */

.metrics {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin-bottom: 22px;
}}

.metric {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
}}

.metric-label {{
    color: var(--muted);
    font-size: 13px;
}}

.metric-value {{
    font-size: 30px;
    font-weight: 700;
    margin-top: 10px;
}}

.metric-critical {{
    color: var(--critical);
}}

.metric-high {{
    color: var(--high);
}}

.metric-medium {{
    color: var(--medium);
}}

.metric-low {{
    color: var(--low);
}}


/* -------------------------------------------------------
   DASHBOARD GRID
------------------------------------------------------- */

.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px;
}}


/* -------------------------------------------------------
   TABLES
------------------------------------------------------- */

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}

th, td {{
    padding: 13px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}}

th {{
    color: var(--muted);
    font-weight: 600;
}}


/* -------------------------------------------------------
   SCANNER STATUS
------------------------------------------------------- */

.status {{
    padding: 5px 9px;
    border-radius: 20px;
    font-size: 11px;
    white-space: nowrap;
}}

.completed_with_findings,
.completed_no_findings {{
    background: #123b31;
    color: #6ee7b7;
}}

.failed {{
    background: #481d27;
    color: #fca5a5;
}}

.not_executed {{
    background: #3b3219;
    color: #fde68a;
}}


/* -------------------------------------------------------
   SEVERITY DISTRIBUTION
------------------------------------------------------- */

.severity-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 17px 0;
}}

.severity-label {{
    width: 110px;
    font-size: 13px;
}}

.severity-track {{
    flex: 1;
    background: #263650;
    height: 10px;
    border-radius: 10px;
    overflow: hidden;
}}

.severity-fill {{
    height: 100%;
    border-radius: 10px;
}}

.severity-count {{
    width: 35px;
    text-align: right;
    font-size: 13px;
}}


/* -------------------------------------------------------
   FILTERS
------------------------------------------------------- */

.filters {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 18px;
}}

input, select {{
    background: var(--panel-light);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 7px;
    padding: 11px;
    min-width: 160px;
}}

input {{
    flex: 1;
    min-width: 220px;
}}


/* -------------------------------------------------------
   FINDINGS
------------------------------------------------------- */

.finding {{
    border: 1px solid var(--border);
    background: var(--panel-light);
    border-radius: 9px;
    margin-bottom: 10px;
    overflow: hidden;
}}

.finding summary {{
    padding: 15px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
    list-style: none;
}}

.finding summary::-webkit-details-marker {{
    display: none;
}}

.finding summary:hover {{
    background: #1c2b43;
}}

.finding-title {{
    flex: 1;
    font-size: 13px;
    font-weight: 600;
    overflow-wrap: anywhere;
}}

.finding-body {{
    padding: 16px;
    border-top: 1px solid var(--border);
    font-size: 13px;
    line-height: 1.7;
}}

.finding-body p {{
    overflow-wrap: anywhere;
    margin: 10px 0;
}}

.finding-body strong {{
    color: #dbeafe;
}}

.finding-body a {{
    color: #60a5fa;
    text-decoration: none;
    overflow-wrap: anywhere;
}}

.finding-body a:hover {{
    text-decoration: underline;
}}


/* -------------------------------------------------------
   FINDING SEVERITY BADGES
------------------------------------------------------- */

.severity {{
    padding: 5px 9px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}}

.sev-critical {{
    background: #481d27;
    color: #fca5a5;
}}

.sev-high {{
    background: #482817;
    color: #fdba74;
}}

.sev-medium {{
    background: #443718;
    color: #fde047;
}}

.sev-low {{
    background: #153c2c;
    color: #86efac;
}}

.sev-informational {{
    background: #123b50;
    color: #7dd3fc;
}}

.sev-unknown {{
    background: #293449;
    color: #cbd5e1;
}}


/* -------------------------------------------------------
   FINDING METADATA
------------------------------------------------------- */

.meta {{
    color: var(--muted);
    font-size: 12px;
    margin-top: 8px;
}}

.empty {{
    color: var(--muted);
    padding: 25px;
    text-align: center;
}}


/* -------------------------------------------------------
   FOOTER
------------------------------------------------------- */

.footer {{
    color: var(--muted);
    font-size: 12px;
    text-align: center;
    padding: 20px;
}}


/* -------------------------------------------------------
   RESPONSIVE LAYOUT
------------------------------------------------------- */

@media (max-width: 900px) {{

    .metrics {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .grid {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 550px) {{

    .container {{
        padding: 15px;
    }}

    .metrics {{
        grid-template-columns: 1fr 1fr;
    }}

    .header h1 {{
        font-size: 21px;
    }}

    .finding summary {{
        flex-wrap: wrap;
    }}
}}

</style>

</head>


<body>

<div class="container">


    <!-- ================================================
         HEADER
    ================================================= -->

    <header class="header">

        <div>

            <h1>Enterprise Application Security</h1>

            <p>Consolidated Security Posture Dashboard</p>

        </div>

        <div class="generated">
            Generated: {report_generated}
        </div>

    </header>


    <!-- ================================================
         EXECUTIVE METRICS
    ================================================= -->

    <section class="metrics">

        <div class="metric">

            <div class="metric-label">
                Total Findings
            </div>

            <div class="metric-value" id="totalFindings">
                0
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                High Findings
            </div>

            <div class="metric-value metric-high" id="highFindings">
                0
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                Critical Findings
            </div>

            <div class="metric-value metric-critical" id="criticalFindings">
                0
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                Scanners Executed
            </div>

            <div class="metric-value" id="scannersExecuted">
                0 / 0
            </div>

        </div>

    </section>


    <!-- ================================================
         SEVERITY AND SCANNER COVERAGE
    ================================================= -->

    <section class="grid">


        <div class="panel">

            <h2 class="section-title">
                Severity Distribution
            </h2>

            <div id="severityChart"></div>

        </div>


        <div class="panel">

            <h2 class="section-title">
                Scanner Coverage
            </h2>

            <table>

                <thead>

                    <tr>
                        <th>Scanner</th>
                        <th>Category</th>
                        <th>Findings</th>
                        <th>Status</th>
                    </tr>

                </thead>

                <tbody>
                    {scanner_rows}
                </tbody>

            </table>

        </div>

    </section>


    <!-- ================================================
         FINDINGS EXPLORER
    ================================================= -->

    <section class="panel">

        <h2 class="section-title">
            Security Findings
        </h2>


        <div class="filters">

            <input
                type="search"
                id="searchInput"
                placeholder="Search findings, rules or files..."
            >


            <select id="scannerFilter">

                <option value="">
                    All Scanners
                </option>

            </select>


            <select id="severityFilter">

                <option value="">
                    All Severities
                </option>

                <option>Critical</option>
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
                <option>Informational</option>
                <option>Unknown</option>

            </select>

        </div>


        <div id="findingCount" class="meta"></div>

        <div id="findingsContainer"></div>

    </section>


    <!-- ================================================
         FOOTER
    ================================================= -->

    <footer class="footer">

        Enterprise AppSec Dashboard |
        Generated from consolidated scanner reports

    </footer>

</div>


<!-- ================================================
     DASHBOARD JAVASCRIPT
================================================= -->

<script>

const reportData = {embedded_data};

const findings = reportData.findings;
const scanners = reportData.scanners;
const summary = reportData.summary;


const severityColors = {{

    Critical: "#ef4444",
    High: "#f97316",
    Medium: "#eab308",
    Low: "#22c55e",
    Informational: "#38bdf8",
    Unknown: "#64748b"

}};


/* ---------------------------------------------------
   HTML ESCAPING
--------------------------------------------------- */

function escapeHTML(value) {{

    return String(value ?? "").replace(/[&<>"']/g, char => ({{

        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"

    }}[char]));

}}


/* ---------------------------------------------------
   SAFE EXTERNAL URL VALIDATION
--------------------------------------------------- */

function safeExternalUrl(value) {{

    if (!value) return "";

    try {{

        const url = new URL(value);

        if (
            url.protocol !== "https:" &&
            url.protocol !== "http:"
        ) {{
            return "";
        }}

        return escapeHTML(url.href);

    }} catch {{

        return "";

    }}

}}


/* ---------------------------------------------------
   SEVERITY CSS CLASS
--------------------------------------------------- */

function severityClass(severity) {{

    return "sev-" +
        String(severity || "Unknown").toLowerCase();

}}


/* ---------------------------------------------------
   EXECUTIVE METRICS
--------------------------------------------------- */

function renderMetrics() {{

    document.getElementById("totalFindings").textContent =
        summary.total;

    document.getElementById("highFindings").textContent =
        summary.severity.High;

    document.getElementById("criticalFindings").textContent =
        summary.severity.Critical;

    const executed = scanners.filter(scanner =>

        scanner.status === "completed_with_findings" ||
        scanner.status === "completed_no_findings"

    ).length;

    document.getElementById("scannersExecuted").textContent =
        executed + " / " + scanners.length;

}}


/* ---------------------------------------------------
   SEVERITY DISTRIBUTION
--------------------------------------------------- */

function renderSeverityChart() {{

    const container =
        document.getElementById("severityChart");

    const max = Math.max(
        ...Object.values(summary.severity),
        1
    );

    container.innerHTML = Object.entries(summary.severity)

        .map(([severity, count]) => {{

            const width = (count / max) * 100;

            return `

                <div class="severity-row">

                    <div class="severity-label">
                        ${{escapeHTML(severity)}}
                    </div>

                    <div class="severity-track">

                        <div
                            class="severity-fill"
                            style="
                                width:${{width}}%;
                                background:${{severityColors[severity]}}
                            "
                        ></div>

                    </div>

                    <div class="severity-count">
                        ${{count}}
                    </div>

                </div>

            `;

        }}).join("");

}}


/* ---------------------------------------------------
   SCANNER FILTER
--------------------------------------------------- */

function populateScannerFilter() {{

    const select =
        document.getElementById("scannerFilter");

    scanners.forEach(scanner => {{

        const option = document.createElement("option");

        option.value = scanner.scanner;

        option.textContent = scanner.scanner;

        select.appendChild(option);

    }});

}}


/* ---------------------------------------------------
   FINDINGS EXPLORER
--------------------------------------------------- */

function renderFindings() {{

    const search = document.getElementById("searchInput")
        .value.toLowerCase();

    const scannerFilter =
        document.getElementById("scannerFilter").value;

    const severityFilter =
        document.getElementById("severityFilter").value;


    const filtered = findings.filter(finding => {{

        const searchable = [

            finding.title,
            finding.rule_id,
            finding.scanner,
            finding.message,
            finding.file,
            finding.remediation,
            finding.cve,
            finding.package

        ].join(" ").toLowerCase();


        const matchesSearch =
            searchable.includes(search);


        const matchesScanner =
            !scannerFilter ||
            finding.scanner === scannerFilter;


        const matchesSeverity =
            !severityFilter ||
            finding.severity === severityFilter;


        return (
            matchesSearch &&
            matchesScanner &&
            matchesSeverity
        );

    }});


    // Sort filtered findings by severity, highest risk first.
    // Unknown or unrecognised severities are placed at the bottom.
    const severityOrder = {{
        Critical: 1,
        High: 2,
        Medium: 3,
        Low: 4,
        Informational: 5,
        Unknown: 6
    }};

    filtered.sort((a, b) => {{
        const severityA = severityOrder[a.severity || "Unknown"] ?? 6;
        const severityB = severityOrder[b.severity || "Unknown"] ?? 6;
        return severityA - severityB;
    }});


    document.getElementById("findingCount").textContent =

        "Showing " + filtered.length +
        " of " + findings.length + " findings";


    const container =
        document.getElementById("findingsContainer");


    if (filtered.length === 0) {{

        container.innerHTML =
            '<div class="empty">No findings match your filters.</div>';

        return;

    }}


    container.innerHTML = filtered.map(finding => {{

        const severity = finding.severity || "Unknown";

        const advisoryUrl =
            safeExternalUrl(finding.advisory_url);


        return `

            <details class="finding">

                <summary>

                    <span class="severity ${{severityClass(severity)}}">

                        ${{escapeHTML(severity)}}

                    </span>


                    <span class="finding-title">

                        ${{escapeHTML(finding.title)}}

                    </span>


                    <span class="meta">

                        ${{escapeHTML(finding.scanner)}}

                    </span>

                </summary>


                <div class="finding-body">


                    <!-- SCANNER INFORMATION -->

                    <p>
                        <strong>Scanner:</strong>
                        ${{escapeHTML(finding.scanner)}}
                    </p>


                    <p>
                        <strong>Category:</strong>
                        ${{escapeHTML(finding.scanner_type)}}
                    </p>


                    <p>
                        <strong>Rule ID:</strong>
                        ${{escapeHTML(finding.rule_id)}}
                    </p>


                    <!-- CVE INFORMATION -->

                    ${{finding.cve ? `

                        <p>
                            <strong>CVE:</strong>
                            ${{escapeHTML(finding.cve)}}
                        </p>

                    ` : ""}}


                    <!-- PACKAGE INFORMATION -->

                    ${{finding.package ? `

                        <p>
                            <strong>Package:</strong>
                            ${{escapeHTML(finding.package)}}
                        </p>

                    ` : ""}}


                    ${{finding.installed_version ? `

                        <p>
                            <strong>Installed Version:</strong>
                            ${{escapeHTML(finding.installed_version)}}
                        </p>

                    ` : ""}}


                    ${{finding.fixed_version ? `

                        <p>
                            <strong>Fixed Version:</strong>
                            ${{escapeHTML(finding.fixed_version)}}
                        </p>

                    ` : ""}}


                    <!-- AFFECTED RESOURCE -->

                    <p>
                        <strong>File / Endpoint:</strong>
                        ${{escapeHTML(finding.file)}}
                    </p>


                    <p>
                        <strong>Line / Method:</strong>
                        ${{escapeHTML(finding.line ?? "N/A")}}
                    </p>


                    <!-- SECURITY SCORE -->

                    ${{finding.security_score !== null &&
                       finding.security_score !== undefined ? `

                        <p>
                            <strong>Security Score:</strong>
                            ${{escapeHTML(finding.security_score)}} / 10
                        </p>

                    ` : ""}}


                    <!-- DESCRIPTION -->

                    <p>

                        <strong>Description:</strong><br>

                        ${{escapeHTML(
                            finding.description ||
                            finding.message ||
                            "No description provided."
                        )}}

                    </p>


                    <!-- REMEDIATION -->

                    <p>

                        <strong>Remediation:</strong><br>

                        ${{escapeHTML(
                            finding.remediation ||
                            "No remediation guidance provided."
                        )}}

                    </p>


                    <!-- SEVERITY -->

                    <p>

                        <strong>Severity:</strong>

                        ${{escapeHTML(finding.severity)}}

                    </p>


                    <!-- ORIGINAL SEVERITY -->

                    ${{finding.original_severity ? `

                        <p>

                            <strong>Original Severity:</strong>

                            ${{escapeHTML(finding.original_severity)}}

                        </p>

                    ` : ""}}


                    <!-- ADVISORY LINK -->

                    ${{advisoryUrl ? `

                        <p>

                            <strong>Security Advisory:</strong>

                            <a
                                href="${{advisoryUrl}}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >

                                View vulnerability advisory ↗

                            </a>

                        </p>

                    ` : ""}}


                    <!-- SARIF LEVEL -->

                    ${{finding.sarif_level ? `

                        <p class="meta">

                            <strong>SARIF Reporting Level:</strong>

                            ${{escapeHTML(finding.sarif_level)}}

                        </p>

                    ` : ""}}


                </div>

            </details>

        `;

    }}).join("");

}}


/* ---------------------------------------------------
   EVENT LISTENERS
--------------------------------------------------- */

document.getElementById("searchInput")

    .addEventListener("input", renderFindings);


document.getElementById("scannerFilter")

    .addEventListener("change", renderFindings);


document.getElementById("severityFilter")

    .addEventListener("change", renderFindings);


/* ---------------------------------------------------
   INITIALIZE DASHBOARD
--------------------------------------------------- */

renderMetrics();

renderSeverityChart();

populateScannerFilter();

renderFindings();

</script>

</body>

</html>
"""


# ---------------------------------------------------------
# COMMAND LINE ENTRY POINT
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Generate Enterprise AppSec HTML Dashboard"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to parsed-findings.json"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output HTML dashboard path"
    )

    args = parser.parse_args()

    input_file = Path(args.input)
    output_file = Path(args.output)

    if not input_file.exists():

        parser.error(
            f"Input file not found: {input_file}"
        )

    data = load_report(input_file)

    html_content = generate_html(data)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file.write_text(
        html_content,
        encoding="utf-8"
    )

    print()

    print("===================================")
    print(" ENTERPRISE APPSEC DASHBOARD")
    print("===================================")

    print(
        f"Total findings: "
        f"{len(data.get('findings', []))}"
    )

    print(
        f"Total scanners: "
        f"{len(data.get('scanners', []))}"
    )

    print(f"Output: {output_file}")

    print("===================================")


if __name__ == "__main__":
    main()
