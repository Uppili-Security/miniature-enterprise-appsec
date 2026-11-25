
# Miniature Enterprise AppSec

An open-source, enterprise-inspired Application Security ecosystem demonstrating how organisations integrate security into the Software Development Life Cycle (SDLC).

This project brings together open-source security tools, DevSecOps practices, vulnerability management, automation, and security reporting into a unified environment.

---

## Architecture

![Miniature Enterprise AppSec Architecture](docs/architecture/appsec-architecture.png)

<details>
<summary>View editable architecture diagram</summary>

[Open architecture diagram](docs/architecture/appsec-architecture.drawio)

</details>

---

## Implemented

| Component | Technology |
|---|---|
| Demo Application | Django, Django REST Framework |
| CI/CD | GitHub Actions |
| SAST | Semgrep |
| SCA | Trivy |
| DAST | OWASP ZAP |
| Secret Scanning | Gitleaks |
| IaC Security | Checkov |
| Container Security | Trivy |
| Security Reporting | Python, SARIF, JSON, HTML |

---

## Security Pipeline

The GitHub Actions workflow executes security scans on pushes and pull requests.

Scan results are collected, normalised, and consolidated into a central security report.

The reporting pipeline generates an interactive HTML dashboard containing:

- Overall vulnerability summary
- Severity distribution
- Scanner coverage and execution status
- Searchable security findings
- Severity and scanner filtering
- Detailed finding information

The dashboard is uploaded as a GitHub Actions artifact.

**Artifact:** `enterprise-security-dashboard`  
**Retention:** 14 days

---

## Vulnerable Demo Application

The Django application contains intentionally vulnerable scenarios to demonstrate security testing and detection capabilities.

### Security Scenarios

- SQL Injection
- Cross-Site Scripting (XSS)
- Server-Side Request Forgery (SSRF)
- Path Traversal
- Command Injection
- Insecure Deserialization
- Broken Object-Level Authorization (BOLA)
- Broken Function-Level Authorization (BFLA)

> ⚠️ This application is intentionally vulnerable and is designed exclusively for local testing and security education. Do not deploy it to production or expose it to the public internet.

---

## Roadmap

### Security Pipeline Enhancements

- [ ] Security quality gates
- [ ] Pull request security feedback
- [ ] Baseline-aware scanning
- [ ] Suppression and exception management
- [ ] GitHub Code Scanning integration
- [ ] Branch protection enforcement

---

## Getting Started

Clone the repository:

```bash
git clone https://github.com/Uppili-Security/miniature-enterprise-appsec.git

cd miniature-enterprise-appsec
```

Run the application locally and execute the security pipeline through GitHub Actions.

Refer to the project structure and workflow files for configuration and implementation details.

---

## Disclaimer

This project is intended for educational purposes and to demonstrate practical Application Security engineering practices.

All vulnerabilities within the demo application are intentional.
