
# Miniature Enterprise AppSec

An open-source, enterprise-inspired Application Security ecosystem demonstrating how organisations integrate security into the Software Development Life Cycle (SDLC).

Miniature Enterprise AppSec brings together open-source security tools, DevSecOps practices, vulnerability management, infrastructure security, automation, and security governance into a unified, reproducible environment.

Rather than demonstrating individual security scanners in isolation, this project focuses on building an integrated Application Security programme inspired by real-world enterprise security operations.

**Project status:** Under active development. Capabilities are implemented incrementally.

---

## Objectives

- Demonstrate an end-to-end enterprise-inspired Application Security programme.
- Integrate security throughout the Software Development Life Cycle.
- Automate security testing within CI/CD pipelines.
- Demonstrate vulnerability discovery, prioritisation, and remediation.
- Secure applications, APIs, containers, infrastructure, and cloud environments.
- Demonstrate security governance and risk management practices.
- Improve developer security experience through automation and self-service.
- Provide reusable reference architectures, configurations, and documentation.

## Current Implementation

The repository currently includes the following components.

| Security Domain | Implementation | Technology |
|---|---|---|
| Sample Application | REST APIs, authentication, projects and tasks | Python, Django, Django REST Framework |
| Authentication | JWT authentication and token management | Simple JWT |
| SAST | Static application security scanning | Semgrep |
| SCA | Dependency vulnerability scanning | Trivy |
| DAST | Dynamic application security testing | OWASP ZAP |
| Secrets Detection | Repository secrets scanning | Gitleaks |
| IaC Security | Terraform misconfiguration scanning | Checkov |
| Container Security | Container image vulnerability and secret scanning | Trivy |
| CI/CD Security | Automated security pipeline | GitHub Actions |

### Security Demonstration Application

The Django application provides a controlled environment for demonstrating application security weaknesses.

Implemented functionality includes:

- User registration and JWT authentication.
- Project CRUD APIs.
- Task CRUD APIs.
- Security demonstration endpoints.

The application also includes intentionally vulnerable scenarios for security testing and learning, including:

- SQL injection demonstrations.
- Blind SQL injection demonstrations.
- Cross-site scripting patterns.
- SSRF-related input handling patterns.
- Path traversal-related input handling patterns.
- Command injection-related patterns.
- Insecure deserialization patterns.
- Broken Object Level Authorization (BOLA).
- Broken Function Level Authorization (BFLA).

Some demonstration endpoints illustrate potentially dangerous coding patterns rather than fully exploitable vulnerabilities. Their limitations and testing methodology should be documented alongside the relevant demonstrations.

**Important:** The vulnerable application and infrastructure fixtures are intended for isolated testing only. They must not be exposed to public networks or deployed to production.

## Security Pipeline

The project uses GitHub Actions to execute automated security checks.

The current pipeline contains six independent jobs:

| Job | Tool | Purpose |
|---|---|---|
| SAST | Semgrep | Identify insecure coding patterns |
| SCA | Trivy | Identify vulnerable dependencies |
| IaC Security | Checkov | Identify Terraform misconfigurations |
| DAST | OWASP ZAP | Test the running Django application |
| Secrets Scanning | Gitleaks | Detect accidentally committed secrets |
| Container Security | Trivy | Scan container images for vulnerabilities and secrets |

Security findings are reported through GitHub Code Scanning where supported. ZAP reports are uploaded as workflow artifacts.

The initial pipeline focuses on detection and reporting. Security enforcement and severity-based blocking will be introduced incrementally.

## Architecture

The intended architecture consists of three interconnected layers.

### 1. Application and Infrastructure Layer

A sample application and supporting infrastructure containing intentionally vulnerable and secure implementations.

### 2. Security Testing and Enforcement Layer

Automated and manual security controls integrated throughout the development and deployment lifecycle.

### 3. Security Operations Layer

Centralised vulnerability management, risk tracking, security governance, automation, and reporting.

The architecture will evolve as additional capabilities are implemented.

## Technology Stack

The project prioritises open-source technologies.

| Security Area | Tools |
|---|---|
| Application | Python, Django, Django REST Framework |
| CI/CD | GitHub Actions |
| SAST | Semgrep, CodeQL |
| SCA | Trivy, OWASP Dependency-Check |
| Secrets Detection | Gitleaks |
| Secrets Management | HashiCorp Vault / OpenBao |
| DAST | OWASP ZAP |
| API Security | OWASP ZAP, Burp Suite Community |
| IaC Security | Checkov |
| Container Security | Trivy |
| SBOM | CycloneDX, SPDX |
| SBOM Management | OWASP Dependency-Track |
| Vulnerability Management | OWASP DefectDojo |
| Artifact Signing | Cosign / Sigstore |
| Automation | n8n |
| Infrastructure | Docker, Terraform, Kubernetes |
| Cloud | AWS |
| Threat Modelling | OWASP Threat Dragon / STRIDE |

The technology stack represents both implemented and planned integrations. Individual components will document their purpose, configuration, limitations, and licensing.

## Project Roadmap

The project will be developed incrementally.

### Foundation and Application Security

- [x] Repository foundation and initial architecture
- [x] Django sample application
- [x] JWT authentication
- [x] Project and Task CRUD APIs
- [x] Security demonstration endpoints
- [x] Dockerfile and container build
- [x] GitHub Actions security pipeline
- [x] SAST integration
- [x] SCA integration
- [x] Secrets detection integration
- [x] DAST integration
- [x] IaC security integration
- [x] Container security integration

### Future Enhancements

- [ ] Secure SDLC and threat modelling
- [ ] Security testing for authentication and authorisation
- [ ] API security testing and automation
- [ ] Security gates and severity-based enforcement
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
- [ ] Security metrics and dashboards
- [ ] Documentation and community release

## Getting Started

The project is currently under development.

### Prerequisites

- Python 3.12+
- Git
- Docker Desktop (for container-related demonstrations)

### Run the Django Application Locally

Clone the repository:

```bash
git clone https://github.com/<your-username>/miniature-enterprise-appsec.git
cd miniature-enterprise-appsec
```

Navigate to the backend:

```bash
cd application/backend
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```powershell
Copy-Item .env.example .env
```

Generate a Django secret key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add the generated value to `.env`:

```env
DJANGO_SECRET_KEY=your-generated-secret-key
```

Apply migrations:

```powershell
python manage.py migrate
```

Start the application:

```powershell
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

The security pipeline is executed through GitHub Actions when changes are pushed or pull requests are opened.

## Security Philosophy

This project follows several core principles:

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

Whether you are an Application Security Engineer, security researcher, developer, or DevSecOps practitioner, you are welcome to contribute.

Please open an issue to discuss significant changes before submitting a pull request.

## Disclaimer

This project is intended for educational purposes, security research, and as a reference implementation of enterprise-inspired Application Security practices.

Intentionally vulnerable applications and infrastructure configurations are provided strictly for controlled testing environments.

Do not expose vulnerable components to public networks or deploy demonstration configurations in production environments.

The project does not claim to provide a complete production-ready enterprise security platform.

## Licence

Distributed under the Apache License 2.0.

See the `LICENSE` file for details.
