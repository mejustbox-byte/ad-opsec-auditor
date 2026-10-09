# Security and data handling

This prerelease analyzes local operator-normalized snapshots only. It does not collect from AD, read credentials, exploit services, execute remediation or contact remote endpoints. Real Windows AD and recovery acceptance tests remain not_run.

Do not attach actual infrastructure exports, credentials, keys, event payloads or private reports to public issues, pull requests or CI. Use minimal hand-authored synthetic examples to reproduce errors. A report pass is limited to the declared facts and scope, not a guarantee of forest security.

For a suspected vulnerability, use the repository's private reporting feature if enabled; otherwise report a minimal non-sensitive description and request a private channel. Never publish a live secret as evidence. Pattern scanning is supplementary and does not prove absence of all sensitive data.
