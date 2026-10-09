# ad-opsec-auditor

Read-only offline Active Directory security posture evidence auditor for Tier 0, AD CS, ACL/delegation, service accounts, NTLM/LDAP/SMB, logging and forest recovery readiness.

**v0.1.0a1 is a prerelease offline analyzer, not a live AD collector.** It evaluates operator-normalized evidence. Synthetic examples and CI do not validate a real forest. All live Windows AD checks remain **not_run**. No credentials, network access, exploit execution or remediation writes are used by the CLI.

## Quick start (Python 3.12, no runtime dependencies)

```sh
python3 -m ad_opsec_auditor --version
python3 -m ad_opsec_auditor validate examples/safe.synthetic.json
python3 -m ad_opsec_auditor audit examples/safe.synthetic.json --format markdown
python3 -m ad_opsec_auditor audit examples/risky.synthetic.json --format json
python3 -m unittest discover -s tests -v
```

Safe example exits 0; risky exits 1; incomplete exits 3; malformed input/I/O errors exit 2. JSON/Markdown reports include evidence, severity, confidence, reasons, remediation and explicit limitations. Existing output files are never overwritten. Actual infrastructure exports and secrets must never enter this public repository or public CI.

- [Installation and usage](docs/user-guide.md)
- [Input contract and baseline rules](docs/input-contract.md) / [JSON Schema](schemas/snapshot-v1.schema.json)
- [Requirements](docs/requirements.md), [threat model](docs/threat-model.md), [architecture](docs/architecture.md)
- [Check matrix](docs/check-matrix.md), [MVP plan](docs/mvp-plan.md), [Windows laboratory runbook](docs/lab.md)
- [ADR-0001](docs/adr/0001-stack.md), [ADR-0002](docs/adr/0002-offline-mvp.md)
- [Development, reproducible builds and CI](docs/development.md), [changelog and release limitations](CHANGELOG.md)

Wheel, source archive and portable Python zipapp are prepared for the GitHub prerelease. Download instructions and offline installation are in the user guide. A pass means the declared evidence met one baseline; it is not a claim that the forest is secure or that recovery works.
