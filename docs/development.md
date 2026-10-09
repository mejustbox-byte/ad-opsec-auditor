# Development

Use the Python version declared in `pyproject.toml`. Install the project and
development dependencies with [INSTALL.md](../INSTALL.md), then run the checks
listed in [CONTRIBUTING.md](../CONTRIBUTING.md).

Example offline commands:

```sh
python3 -m unittest discover -s tests -v
python3 -m ad_opsec_auditor validate examples/safe.synthetic.json
python3 -m ad_opsec_auditor audit examples/safe.synthetic.json --format markdown
```

Keep credentials, real domain exports, hostnames, and account data outside the
source tree. Unit tests use synthetic inputs. Live Active Directory validation
requires a separate authorized Windows laboratory.
