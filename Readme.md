# Miniature Enterprise AppSec

An open-source, enterprise-inspired Application Security ecosystem demonstrating how organisations integrate security into the Software Development Life Cycle (SDLC).

Miniature Enterprise AppSec brings together open-source security tools, DevSecOps practices, automated vulnerability discovery, security reporting, and developer-focused workflows in a unified, reproducible environment.

Rather than demonstrating individual scanners in isolation, this project focuses on building an integrated Application Security programme inspired by real-world enterprise security operations.

> **Project status:** Under active development. The Django demonstration application, six-scanner GitHub Actions pipeline, and consolidated HTML security dashboard are implemented. Additional security capabilities are planned.

---

## Table of contents

- [Objectives](#objectives)
- [Architecture](#architecture)
- [Current implementation](#current-implementation)
- [Security demonstration application](#security-demonstration-application)
- [Security pipeline](#security-pipeline)
- [Consolidated security dashboard](#consolidated-security-dashboard)
- [Technology stack](#technology-stack)
- [Getting started](#getting-started)
- [Project roadmap](#project-roadmap)
- [Security philosophy](#security-philosophy)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)

## Objectives

- Demonstrate an end-to-end, enterprise-inspired Application Security programme.
- Integrate security testing into the software development lifecycle.
- Automate security checks within CI/CD pipelines.
- Demonstrate vulnerability discovery, reporting, and remediation workflows.
- Cover application, dependency, infrastructure-as-code, and container security.
- Make security results easier for developers and security teams to understand.
- Provide reusable examples, configurations, architecture, and documentation.

## Architecture

The diagram below illustrates the currently implemented workflow: developer changes trigger GitHub Actions, six security scanners produce reports, and the Python reporting engine consolidates the results into a downloadable HTML dashboard.

![Miniature Enterprise AppSec architecture](docs/architecture/appsec-architecture.png)

The editable source diagram is available here: [`appsec-architecture.drawio`](docs/architecture/appsec-architecture.drawio).

### High-level workflow

1. A developer pushes code or opens a pull request.
2. GitHub Actions starts the security pipeline.
3. Six scanner jobs run: Semgrep, Trivy filesystem, Checkov, OWASP ZAP, Gitleaks, and Trivy container scanning.
4. Available scanner reports are collected as workflow artifacts.
5. Python reporting scripts parse and consolidate the findings.
6. The dashboard generator creates an interactive HTML report.
7. GitHub Actions publishes the dashboard as the `enterprise-security-dashboard` artifact.

The diagram distinguishes the current implementation from future extensions. Planned capabilities are not represented as operational integrations.

## Current implementation

| Area | Component | Technology | Status |
|---|---|---|---|
| Sample application | REST APIs and project/task functionality | Python, Django, Django REST Framework | Implemented |
| Authentication | JWT authentication and token management | Simple JWT | Implemented |
| SAST | Static application security testing | Semgrep | Integrated in CI |
| SCA | Dependency vulnerability scanning | Trivy filesystem | Integrated in CI |
| DAST | Dynamic testing of the running application | OWASP ZAP | Integrated in CI |
| Secrets detection | Repository secret scanning | Gitleaks | Integrated in CI |
| IaC security | Infrastructure-as-code misconfiguration scanning | Checkov | Integrated in CI |
| Container security | Container image vulnerability and secret scanning | Trivy | Integrated in CI |
| CI/CD | Automated pipeline on pushes and pull requests | GitHub Actions | Implemented |
| Reporting | Scanner report collection and parsing | Python, SARIF, JSON | Implemented |
| Dashboard | Consolidated interactive security report | Python, HTML, JavaScript | Implemented |

## Security demonstration application

The Django application provides a controlled environment for demonstrating application security weaknesses.

Implemented application functionality includes:

- User registration and JWT authentication.
- Project CRUD APIs.
- Task CRUD APIs.
- Security demonstration endpoints.

The application includes intentionally vulnerable scenarios for security testing and learning, including:

- SQL injection and blind SQL injection demonstrations.
- Cross-site scripting (XSS) patterns.
- Server-side request forgery (SSRF)-related input handling patterns.
- Path traversal-related input handling patterns.
- Command injection-related patterns.
- Insecure deserialization patterns.
- Broken Object Level Authorization (BOLA).
- Broken Function Level Authorization (BFLA).

Some endpoints demonstrate potentially dangerous coding patterns rather than fully exploitable vulnerabilities. The limitations and validation steps should be documented alongside each demonstration.

> **Safety warning:** The vulnerable application is intended for isolated testing and education only. Do not expose it to public networks or deploy it in production.

## Security pipeline

The GitHub Actions workflow runs on pushes and pull requests across branches. It contains six scanner jobs and a consolidated reporting job.

| Job | Tool | Purpose |
|---|---|---|
| SAST | Semgrep | Identify insecure coding patterns |
| SCA | Trivy | Identify vulnerable application dependencies |
| IaC security | Checkov | Identify infrastructure-as-code misconfigurations |
| DAST | OWASP ZAP | Test the running Django application |
| Secrets scanning | Gitleaks | Detect accidentally committed secrets |
| Container security | Trivy | Scan container images for vulnerabilities and secrets |
| Consolidated reporting | Python scripts | Collect scanner reports and generate the HTML dashboard |

### Pipeline execution

1. GitHub Actions starts the scanner jobs for a push or pull request.
2. Scanner jobs execute independently and upload their available reports as workflow artifacts. SARIF results are also uploaded to GitHub Code Scanning where configured and supported.
3. The reporting job runs after the scanner jobs, including when one or more scanner jobs fail.
4. The reporting job downloads available scanner artifacts into a common directory structure.
5. The Python parser processes SARIF and OWASP ZAP JSON reports and creates consolidated findings in JSON.
6. The dashboard generator converts the consolidated findings into an interactive HTML report.
7. The HTML dashboard is uploaded as the `enterprise-security-dashboard` workflow artifact.

The dashboard artifact has a **14-day retention period**. Download it from the **Artifacts** section of the relevant GitHub Actions workflow run. The dashboard is not currently embedded directly in pull request conversations.

The initial pipeline focuses on detection and reporting. Severity-based enforcement and security gates are future enhancements. A successful workflow run means the jobs completed; it does not mean the scanned code is free of security findings.

## Consolidated security dashboard

The reporting implementation is maintained in `security-reporting/`.

| File | Responsibility |
|---|---|
| `generate_report.py` | Discovers and parses scanner SARIF/JSON reports and consolidates findings |
| `generate_dashboard.py` | Generates the interactive HTML security dashboard |
| `requirements.txt` | Python dependencies for the reporting scripts |

The dashboard currently provides:

- Executive summary metrics, including total findings and severity counts.
- Scanner coverage and execution status.
- Findings ordered by severity.
- Scanner and severity filters.
- Text search across findings.
- Expandable finding details, including available vulnerability identifiers, affected packages or resources, descriptions, and remediation guidance.

The parser uses severity metadata supplied by scanner reports where available. Findings without reliable severity metadata are retained as **Unknown** rather than being assigned an assumed severity.

### Generate the dashboard locally

Run the scanners or place their supported output files under `security-reporting/scan-reports/`, using the scanner-specific directory structure expected by the parser.

From the repository root, run:

```bash
python security-reporting/generate_report.py \
  --input security-reporting/scan-reports \
  --output security-reporting/parsed-findings.json
```

Then generate the HTML dashboard:

```bash
python security-reporting/generate_dashboard.py \
  --input security-reporting/parsed-findings.json \
  --output security-reporting/enterprise-security-report.html
```

Open `security-reporting/enterprise-security-report.html` in a web browser.

Generated scanner reports, consolidated JSON, and HTML output are local/generated artifacts and should not be committed as source files.

## Technology stack

The table below separates technologies already integrated from potential future additions.

| Security area | Technology | Status |
|---|---|---|
| Application | Python, Django, Django REST Framework | Implemented |
| CI/CD | GitHub Actions | Implemented |
| SAST | Semgrep | Implemented |
| SCA | Trivy | Implemented |
| DAST | OWASP ZAP | Implemented |
| Secrets detection | Gitleaks | Implemented |
| IaC security | Checkov | Implemented |
| Container security | Trivy | Implemented |
| Reporting | Python, SARIF, JSON, HTML | Implemented |
| Additional SAST | CodeQL | Planned |
| Additional SCA | OWASP Dependency-Check | Planned |
| Secrets management | HashiCorp Vault / OpenBao | Planned |
| SBOM | CycloneDX / SPDX | Planned |
| SBOM management | OWASP Dependency-Track | Planned |
| Vulnerability management | OWASP DefectDojo | Planned |
| Artifact signing | Cosign / Sigstore | Planned |
| Automation | n8n | Planned |
| Infrastructure | Docker, Terraform, Kubernetes | Kubernetes integration planned |
| Cloud security | AWS security scenarios | Planned |
| Threat modelling | OWASP Threat Dragon / STRIDE | Planned |
| API security | Expanded API security testing workflows | Planned |

## Getting started

The project is under active development. The following steps describe how to run the Django demonstration application locally.

### Prerequisites

- Python 3.12 or later.
- Git.
- Docker Desktop (for container-related demonstrations).

### 1. Clone the repository

```bash
git clone https://github.com/Uppili-Security/miniature-enterprise-appsec.git
cd miniature-enterprise-appsec
```

### 2. Navigate to the backend

```bash
cd application/backend
```

### 3. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

If the repository contains `.env.example`, copy it to `.env`:

```powershell
Copy-Item .env.example .env
```

Generate a Django secret key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add the generated value to `.env`:

```dotenv
DJANGO_SECRET_KEY=your-generated-secret-key
```

Use the other environment variables required by the application configuration as appropriate. Never commit real secrets.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Start the application

```bash
python manage.py runserver
```

The development server is available at:

```text
http://127.0.0.1:8000/
```

The security pipeline runs through GitHub Actions when changes are pushed or pull requests are opened. Download the consolidated dashboard from the Artifacts section of the corresponding workflow run.

## Project roadmap

Checkmarks indicate capabilities currently implemented in the repository. Unchecked items are future work.

### Foundation and application security

- [x] Repository foundation and initial architecture.
- [x] Django sample application.
- [x] JWT authentication.
- [x] Project and task CRUD APIs.
- [x] Security demonstration endpoints.
- [x] Dockerfile and container build.
- [x] GitHub Actions security pipeline.
- [x] SAST integration (Semgrep).
- [x] SCA integration (Trivy).
- [x] Secrets detection (Gitleaks).
- [x] DAST integration (OWASP ZAP).
- [x] IaC security integration (Checkov).
- [x] Container security integration (Trivy).
- [x] Scanner report collection and parsing.
- [x] Consolidated security findings JSON.
- [x] Interactive HTML security dashboard.
- [x] Dashboard artifact publishing in GitHub Actions.

### Future enhancements

- [ ] Secure SDLC and threat modelling.
- [ ] Expanded authentication and authorisation testing.
- [ ] API security testing and automation.
- [ ] Security gates and severity-based enforcement.
- [ ] Pull request security feedback and introduced-finding analysis.
- [ ] Kubernetes security.
- [ ] Cloud security.
- [ ] SBOM generation and software supply-chain security.
- [ ] Secrets and cryptographic key management.
- [ ] Centralised vulnerability management.
- [ ] Application Security Posture Management (ASPM).
- [ ] Security governance and risk management.
- [ ] Security operations and incident response.
- [ ] Security automation and developer experience.
- [ ] Security Champions programme.
- [ ] AI-powered security assistant.
- [ ] Advanced security metrics and dashboards.

## Security philosophy

This project is guided by the following principles:

- Security by design.
- Shift-left and continuous security.
- Risk-based vulnerability prioritisation.
- Least privilege and zero-trust principles.
- Defence in depth.
- Developer-friendly security controls.
- Continuous monitoring and improvement.
- Security automation and measurable outcomes.

## Contributing

Contributions, suggestions, feature requests, and improvements are welcome.

Whether you are an Application Security Engineer, security researcher, developer, or DevSecOps practitioner, you are welcome to contribute. For significant changes, please open an issue to discuss the proposal before submitting a pull request.

## Disclaimer

This project is intended for educational purposes, security research, and as a reference implementation of enterprise-inspired Application Security practices.

Intentionally vulnerable applications and infrastructure configurations are provided strictly for controlled testing environments. Do not expose vulnerable components to public networks or deploy demonstration configurations in production environments.

This project is a learning and reference environment; it does not claim to provide a complete, production-ready enterprise security platform.


