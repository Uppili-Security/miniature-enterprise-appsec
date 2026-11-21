Miniature Enterprise AppSec
An open-source, enterprise-inspired Application Security ecosystem
demonstrating how organisations integrate security into the Software
Development Life Cycle (SDLC).

Miniature Enterprise AppSec brings together open-source security tools,
DevSecOps practices, vulnerability management, infrastructure security,
automation, and security governance into a unified, reproducible
environment.

Rather than demonstrating individual security scanners in isolation,
this project focuses on building an integrated Application Security
programme inspired by real-world enterprise security operations.

Project status: Under active development. The foundation,
six-scanner GitHub Actions pipeline, and consolidated HTML security
dashboard are implemented. Additional capabilities are being developed
incrementally.
Objectives
- Demonstrate an end-to-end enterprise-inspired Application Security
  programme.
- Integrate security throughout the Software Development Life Cycle.
- Automate security testing within CI/CD pipelines.
- Demonstrate vulnerability discovery, prioritisation, and
  remediation.
- Secure applications, APIs, containers, infrastructure, and cloud
  environments.
- Demonstrate security governance and risk management practices.
- Improve developer security experience through automation and
  self-service.
- Provide reusable reference architectures, configurations, and
  documentation.
Current Implementation
The repository currently includes the following components.
  Security Domain   Implementation     Technology        Status
  Sample            REST APIs and      Python, Django,   Implemented
Application       authentication,    Django REST
with project/task  Framework
functionality                        

  Authentication    JWT authentication Simple JWT        Implemented
and token
management                           

  SAST              Static application Semgrep           Integrated in CI
security scanning                    

  SCA               Dependency         Trivy             Integrated in CI
vulnerability
scanning                             

  DAST              Dynamic            OWASP ZAP         Integrated in CI
application
security testing
against the
running Django
application                          

  Secrets Detection Repository secrets Gitleaks          Integrated in CI
scanning                             

  IaC Security      Terraform          Checkov           Integrated in CI
misconfiguration
scanning                             

  Container         Container image    Trivy             Integrated in CI
Security          vulnerability and
secret scanning                      

  CI/CD Security    Automated security GitHub Actions    Implemented
pipeline on pushes
and pull requests                    

  Security          Collection and     Python, SARIF,    Implemented
Reporting         parsing of scanner JSON
output                               
Security          Consolidated       Python, HTML,     Implemented
Dashboard         interactive HTML   JavaScript
dashboard uploaded
as a workflow
artifact
Security Demonstration Application
The Django application provides a controlled environment for
demonstrating application security weaknesses.

Implemented functionality includes:
- User registration and JWT authentication.
- Project CRUD APIs.
- Task CRUD APIs.
- Security demonstration endpoints.
The application also includes intentionally vulnerable scenarios for
security testing and learning, including:
- SQL injection demonstrations.
- Blind SQL injection demonstrations.
- Cross-site scripting patterns.
- SSRF-related input handling patterns.
- Path traversal-related input handling patterns.
- Command injection-related patterns.
- Insecure deserialization patterns.
- Broken Object Level Authorization (BOLA).
- Broken Function Level Authorization (BFLA).
Some demonstration endpoints illustrate potentially dangerous coding
patterns rather than fully exploitable vulnerabilities. Their
limitations and testing methodology should be documented alongside the
relevant demonstrations.

Important: The vulnerable application and infrastructure fixtures
are intended for isolated testing only. They must not be exposed to
public networks or deployed to production.
Security Pipeline
The project uses GitHub Actions to execute automated security checks.
The workflow runs on pushes and pull requests across branches.

The pipeline contains six independent scanner jobs and a consolidated
reporting job.
  Job                     Tool                    Purpose
  SAST                    Semgrep                 Identify insecure
coding patterns

  SCA                     Trivy                   Identify vulnerable
application
dependencies

  IaC Security            Checkov                 Identify Terraform
misconfigurations

  DAST                    OWASP ZAP               Test the running Django
application

  Secrets Scanning        Gitleaks                Detect accidentally
committed secrets

  Container Security      Trivy                   Scan container images
for vulnerabilities and
secrets
Consolidated Reporting  Python reporting        Collect scanner
scripts                 artifacts and generate
the HTML dashboard
Pipeline behaviour
1. GitHub Actions starts the scanner jobs for a push or pull request.
2. Scanner jobs execute independently and upload their available
   reports as workflow artifacts. SARIF results are also uploaded to
   GitHub Code Scanning where configured and supported.
3. The reporting job runs after the scanner jobs, including when one or
   more scanner jobs fail.
4. The reporting job downloads available scanner artifacts into a
   common directory structure.
5. The Python parser processes SARIF and OWASP ZAP JSON reports and
   produces consolidated findings in JSON.
6. The dashboard generator converts the consolidated findings into an
   interactive HTML report.
7. The HTML dashboard is uploaded as the
   enterprise-security-dashboard workflow artifact.
The dashboard artifact is configured with a 14-day retention period. It
can be downloaded from the Artifacts section of the relevant GitHub
Actions workflow run. It is not currently embedded directly in the pull
request conversation.

The initial pipeline focuses on detection and reporting. Security
enforcement and severity-based blocking will be introduced
incrementally. A successful workflow run indicates that the jobs
completed; it does not mean that the scanned code has no security
findings.
Consolidated Security Dashboard
The reporting implementation is maintained under security-reporting/.
  File                                Responsibility
  generate_report.py                Discovers and parses scanner
SARIF/JSON reports and consolidates
findings

  generate_dashboard.py             Generates the interactive HTML
security dashboard
requirements.txt                  Python dependencies used by the
reporting scripts
The dashboard currently provides:
- Executive summary metrics, including total findings and severity
  counts.
- Scanner coverage and execution status.
- Findings grouped and ordered by severity.
- Scanner and severity filters.
- Text search across findings.
- Expandable finding details, including available vulnerability
  identifiers, affected packages/resources, descriptions, and
  remediation guidance.
The parser uses severity metadata supplied by scanner reports where
available. Findings without reliable severity metadata are retained as
Unknown rather than being assigned an assumed severity.
Generate the dashboard locally
Run the scanners or place their supported output files under
security-reporting/scan-reports/ using the scanner-specific directory
structure expected by the parser.

From the repository root, run:
python security-reporting/generate_report.py \
  --input security-reporting/scan-reports \
  --output security-reporting/parsed-findings.json
Then generate the HTML dashboard:
python security-reporting/generate_dashboard.py \
  --input security-reporting/parsed-findings.json \
  --output security-reporting/enterprise-security-report.html
Open security-reporting/enterprise-security-report.html in a web
browser.

Generated scanner reports, consolidated JSON, and HTML output are
local/generated artifacts and should not be committed as source files.
Architecture
The diagram below shows the currently implemented application security workflow, from developer changes through automated scanning, report consolidation, and dashboard publication.

The editable draw.io source is available at [`docs/architecture/appsec-architecture.drawio`](docs/architecture/appsec-architecture.drawio).
Architecture flow
1. Developers push changes or open pull requests.
2. GitHub Actions runs the six integrated security scanners: Semgrep, Trivy filesystem (SCA), Checkov, OWASP ZAP, Gitleaks, and Trivy container scanning.
3. Scanner outputs are collected as workflow artifacts in supported SARIF and JSON formats.
4. The Python reporting scripts parse and consolidate the available results.
5. The dashboard generator creates an interactive HTML security dashboard.
6. GitHub Actions publishes the dashboard as the enterprise-security-dashboard artifact, with a 14-day retention period.
The Django demonstration application is the application under test. The dashed future-extension area in the diagram represents planned capabilities, not currently implemented integrations.

Current implementation: The sample Django application, six-scanner GitHub Actions pipeline, and consolidated reporting dashboard form the initial working implementation. Broader security operations and governance capabilities remain part of the project direction.
Technology Stack
The project prioritises open-source technologies.
  Security Area                       Tools
  Application                         Python, Django, Django REST
Framework

  CI/CD                               GitHub Actions

  SAST                                Semgrep, CodeQL (planned)

  SCA                                 Trivy, OWASP Dependency-Check
(planned)

  Secrets Detection                   Gitleaks

  Secrets Management                  HashiCorp Vault / OpenBao (planned)

  DAST                                OWASP ZAP

  API Security                        OWASP ZAP, Burp Suite Community
(planned integration/workflow)

  IaC Security                        Checkov

  Container Security                  Trivy

  SBOM                                CycloneDX, SPDX (planned)

  SBOM Management                     OWASP Dependency-Track (planned)

  Vulnerability Management            OWASP DefectDojo (planned)

  Artifact Signing                    Cosign / Sigstore (planned)

  Automation                          n8n (planned)

  Infrastructure                      Docker, Terraform, Kubernetes
(Kubernetes integration planned)

  Cloud                               AWS (planned security scenarios)

  Threat Modelling                    OWASP Threat Dragon / STRIDE
(planned)
Reporting                           Python, SARIF, JSON, HTML
The technology stack represents both implemented and planned
integrations. Individual components will document their purpose,
configuration, limitations, and licensing.
Project Roadmap
The project will be developed incrementally. Checkmarks indicate
capabilities currently implemented in the repository and pipeline;
unchecked items remain future work.
Foundation and Application Security
- [x] Repository foundation and initial architecture
- [x] Django sample application
- [x] JWT authentication
- [x] Project and Task CRUD APIs
- [x] Security demonstration endpoints
- [x] Dockerfile and container build
- [x] GitHub Actions security pipeline
- [x] SAST integration (Semgrep)
- [x] SCA integration (Trivy)
- [x] Secrets detection integration (Gitleaks)
- [x] DAST integration (OWASP ZAP)
- [x] IaC security integration (Checkov)
- [x] Container security integration (Trivy)
- [x] Scanner report collection and parsing
- [x] Consolidated security findings JSON generation
- [x] Interactive HTML security dashboard
- [x] Dashboard artifact publishing in GitHub Actions
- [x] Dashboard generation on push, pull request, and merge-triggered
  workflow runs
Future Enhancements
- [ ] Secure SDLC and threat modelling
- [ ] Security testing for authentication and authorisation
- [ ] API security testing and automation
- [ ] Security gates and severity-based enforcement
- [ ] PR-level security feedback and introduced-finding analysis
- [ ] Kubernetes security
- [ ] Cloud security
- [ ] SBOM generation and software supply-chain security
- [ ] Secrets and cryptographic key management
- [ ] Centralised vulnerability management
- [ ] Application Security Posture Management (ASPM)
- [ ] Security governance and risk management
- [ ] Security operations and incident response
- [ ] Security automation and developer experience
- [ ] Security Champions programme
- [ ] AI-powered security assistant
- [ ] Advanced security metrics and dashboards
- [ ] Documentation and community release
Getting Started
The project is currently under development.
Prerequisites
- Python 3.12+
- Git
- Docker Desktop (for container-related demonstrations)
Run the Django Application Locally
Clone the repository:
git clone https://github.com/Uppili-Security/miniature-enterprise-appsec.git
cd miniature-enterprise-appsec
Navigate to the backend:
cd application/backend
Create and activate a virtual environment:
python -m venv .venv
Windows PowerShell:
.\\.venv\\Scripts\\Activate.ps1
Install dependencies:
pip install -r requirements.txt
Create your environment file:
Copy-Item .env.example .env
Generate a Django secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
Add the generated value to .env:
DJANGO_SECRET_KEY=your-generated-secret-key
Apply migrations:
python manage.py migrate
Start the application:
python manage.py runserver
The application will be available at:
http://127.0.0.1:8000/
The security pipeline is executed through GitHub Actions when changes
are pushed or pull requests are opened. The consolidated dashboard can
be downloaded from the Artifacts section of the corresponding workflow
run.
Security Philosophy
This project follows several core principles:
- Security by design.
- Shift-left and continuous security.
- Risk-based vulnerability prioritisation.
- Least privilege and zero-trust principles.
- Defence in depth.
- Developer-friendly security controls.
- Continuous monitoring and improvement.
- Security automation and measurable outcomes.
Contributing
Contributions, suggestions, feature requests, and improvements are
welcome.

Whether you are an Application Security Engineer, security researcher,
developer, or DevSecOps practitioner, you are welcome to contribute.

Please open an issue to discuss significant changes before submitting a
pull request.
Disclaimer
This project is intended for educational purposes, security research,
and as a reference implementation of enterprise-inspired Application
Security practices.

Intentionally vulnerable applications and infrastructure configurations
are provided strictly for controlled testing environments.

Do not expose vulnerable components to public networks or deploy
demonstration configurations in production environments.

The project does not claim to provide a complete production-ready
enterprise security platform.
