# Normalized snapshot v1 и baseline-v1

Полная [JSON Schema](../schemas/snapshot-v1.schema.json) поставляется в package и выводится CLI `schema`. Input ≤2 MiB UTF-8, depth ≤16. Неизвестные поля, duplicate keys, non-finite numbers, unpaired Unicode surrogates, control characters и неподходящие типы запрещены. Все timestamps строго `YYYY-MM-DDTHH:MM:SSZ`; evidence не новее collected_at snapshot. До 500 evidence, 1000 templates, integer counts 0…1,000,000. Runtime дополнительно проверяет semantic references и collection consistency; одной JSON Schema недостаточно.

## Верхний уровень

Обязательны schema_version=1, synthetic boolean, scope (1…256 chars), collected_at, source (1…128 chars), evidence array и observations object. synthetic=true — заявленный вымышленный input; false — operator-supplied-unverified. Ни флаг, ни hash не подтверждают provenance. Scope может обозначать конкретную согласованную область, не автоматически весь лес.

Evidence entry: id (1…64 ASCII letters/digits/`_.:-`, первый alphanumeric), source, collected_at и description (до 512 chars). ID уникален; evidence_refs разрешаются только по этому массиву и никогда не открываются как path или URL. Report включает лишь используемые записи.

Observation keyed по одному из девяти check ID: state (`collected`, `unknown`, `not_run`), coverage (`complete`, `partial`, `none`), reason, evidence_refs и facts. Для unknown/not_run: coverage=none, пустые facts и refs, непустая reason. Для collected: complete/partial; partial требует reason. Отсутствующий check = not_run. Collected без всех facts или evidence = unknown. Нельзя подать готовый finding/pass и заставить анализатор его принять.

## Нормализация и scope каждого факта

Ниже facts — вывод доверенного оператора по независимым источникам, не значения, самостоятельно полученные CLI. Boolean относится ко **всем** scoped relevant endpoints, а counts — к полному утверждённому scope. Отсутствующие знания выражать отсутствием fact или partial coverage, а не нулём/false. Не обобщать результат одного DC на весь лес. Complete означает, что оператор проверил необходимую полноту; analyzer её независимо не удостоверяет.

| Check | Facts | Safe baseline |
| --- | --- | --- |
| T0-01 | unexpected_admin_paths, unapproved_privileged_members | оба count = 0, утверждённый Tier 0 scope |
| CS-01 | unprivileged_ca_control; templates array | нет CA control для unprivileged; ни один template не соответствует полной рискованной комбинации |
| ACL-01 | unauthorized_control_edges, unresolved_aces | оба count = 0; unresolved >0 даёт unknown если нет известного нарушения |
| SVC-01 | unmanaged_privileged_accounts, stale_accounts, unrestricted_gmsa_readers | все count = 0; stale определяется утверждённым lifecycle policy оператора |
| NTLM-01 | effective_restriction, observed_ntlm | true / false; наблюдение только в указанном source/evidence window, не обещание отсутствия NTLM везде |
| LDAP-01 | effective_signing_required, effective_channel_binding_required | оба true, effective policy для всех scoped endpoints |
| SMB-01 | effective_signing_required, smb1_enabled | true / false |
| LOG-01 | effective_advanced_audit, forwarding_healthy, retention_days | true / true / ≥30 дней |
| REC-01 | runbook_reviewed, backup_verified, isolated_drill_succeeded, drill_age_days | true / true / true / ≤180 дней на collected_at |

Template fields обязательны: name, published, authentication, enrollee_supplies_subject, unprivileged_enrollment, approval_required (boolean), authorized_signatures (count). Risk combination: published AND authentication AND enrollee_supplies_subject AND unprivileged_enrollment AND NOT approval_required AND authorized_signatures=0. Это узкий ESC1-style configuration warning, **не полная ESC1 exploitability или полное покрытие ESC2…ESC16**. Непривилегированный CA control отдельно даёт fail. Пустой templates inventory без CA finding даёт unknown, а не pass.

Logging baseline 30 дней и recovery 180 дней фиксированы в baseline-v1; это проектная политика, не универсальный Microsoft compliance стандарт. Stale classification, unexpected paths и unauthorized edges требуют явно выбранного baseline и evidence description. Native ACE semantics и cross-domain graph не вычисляются в этом MVP.

## Результаты и доверие

Каждый result: check_id/rule_id, status, severity, risk_severity, confidence, coverage, evidence_refs, reason, violations, remediation, limitations. Severity для fail — risk severity правила; для остальных info, potential risk отдельно в risk_severity. Confidence для pass/fail medium (непроверенная provenance), unknown/not_run low. Partial coverage всегда unknown даже при известных risk facts: исходный риск нужно отдельно проверить, нельзя читать unknown как здоровый результат. Наличие known unauthorized ACL edge даёт fail даже при unresolved ACE, но не обещает полный effective access graph.

Report_schema_version=1, engine/rules version, SHA256 exact input bytes, scope/time/source, synthetic/provenance/warning, summary и referenced evidence. Два запуска тех же bytes с той же версией дают identical output. Equivalent JSON с другим whitespace имеет другой hash. Remediation — только текст, не команда исправления.
