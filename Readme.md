Miniature Enterprise AppSec
An open-source project demonstrating an end-to-end Application Security
workflow by integrating security testing into CI/CD, consolidating
findings, and providing actionable security visibility.
Architecture

Editable diagram:
[`appsec-architecture.drawio`](docs/architecture/appsec-architecture.drawio)
Implemented
  Security area        Technology                              Status
  Application          Python, Django, Django REST Framework   Implemented
CI/CD                GitHub Actions                          Implemented
SAST                 Semgrep                                 Implemented
SCA                  Trivy                                   Implemented
DAST                 OWASP ZAP                               Implemented
Secrets detection    Gitleaks                                Implemented
IaC security         Checkov                                 Implemented
Container security   Trivy                                   Implemented
Reporting            Python, SARIF, JSON, HTML               Implemented
Security pipeline
GitHub Actions runs the security scanners on pushes and pull requests.
Scanner reports are collected and processed by Python reporting scripts
into consolidated findings and an interactive HTML dashboard.

The dashboard provides: - Summary metrics and severity breakdown. -
Scanner coverage and execution status. - Search and severity/scanner
filters. - Detailed findings and remediation information.

Download the enterprise-security-dashboard artifact from the relevant
Actions run (14-day retention).
Demonstration application
The Django application includes authentication, project/task APIs, and
intentionally vulnerable scenarios for security testing, including SQL
injection, XSS, SSRF, path traversal, command injection, insecure
deserialization, BOLA, and BFLA.
Warning: This application is for isolated security testing only.
Do not expose it publicly or deploy it to production.

Roadmap
The next phase focuses exclusively on strengthening security enforcement
and developer feedback.
- [ ] Security quality gates
- [ ] Pull request security feedback
- [ ] Baseline-aware scanning
- [ ] Suppression and exception management
- [ ] GitHub Code Scanning integration
- [ ] Branch protection enforcement
Getting started
Prerequisites
- Python 3.12+
- Git
- Docker Desktop (for container testing)
Run the application
git clone https://github.com/Uppili-Security/miniature-enterprise-appsec.git
cd miniature-enterprise-appsec/application/backend

python -m venv .venv
Activate the virtual environment (PowerShell):
.\.venv\Scripts\Activate.ps1
Install dependencies and run:
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Visit http://127.0.0.1:8000/.
Disclaimer
This project is an educational and reference implementation of
enterprise-inspired AppSec practices. Intentionally vulnerable
components are provided for controlled testing only.
