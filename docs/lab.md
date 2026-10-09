# Изолированный Windows-стенд

## Топология и предпосылки

Отдельная виртуальная сеть без маршрута в production; домен lab.example.test. DC1 и DC2: Windows Server 2022 AD DS/DNS; CA1: отдельная enterprise issuing CA; MEMBER1: member server для SMB/service policy; MGMT1: Windows management host с Windows PowerShell 5.1 и RSAT ActiveDirectory/GroupPolicy. Второй домен и trust добавляются для cross-domain ACL после базового стенда. Server 2019/2025 — отдельные будущие compatibility runs. Образы и лицензии предоставляет владелец стенда; Linux cloud не заменяет их.

Минимально планировать 5 VM, 2 vCPU и 4 GiB RAM на VM, CA/DC хранилище от 60 GiB, затем уточнить по нагрузке. Синхронизация времени и DNS обязательны. Scope allowlist включает только lab hosts. Доступность LDAP/LDAPS, Kerberos, DNS, SMB и требуемого management transport проверяется внутри лаборатории; порты не публикуются в Интернет. WinRM не открывается автоматически. HTTPS management проверяет доверенную цепочку, NTLM fallback не включается ради успешного теста.

## Роли и данные

Lab admin отдельно создаёт конфигурации и checkpoints. AuditReader — отдельная непривилегированная учётная запись; delegated read/event access добавляется по источнику и фиксируется. Не давать Domain Admin как обход ошибки. Credentials вводятся только средствами Windows/secure settings, не в Git, fixture или shell arguments. Даже тестовые секреты не коммитятся.

Данные полностью вымышлены: группы Tier0-Lab, svc-demo, template LabTemplate; SIDs и memberships создаются только в этом лесу. Все выгрузки хранятся в частном lab directory с ограниченным ACL, без upload в Actions. Public fixtures создаются вручную из модели, а не копированием exports.

## Последовательность валидации после реализации

1. Владелец создаёт snapshot/checkpoint до сценария и записывает OS/module/build версии.
2. Администратор настраивает safe baseline и один намеренно рискованный вариант для каждого check матрицы. Изменения выполняются подготовкой стенда, не аудитором.
3. Оператор фиксирует scope, account SID и минимальные права; проверяет read prerequisites. Отказ доступа должен дать unknown.
4. Запускает будущий collector с budget, сохраняет stdout/stderr без secrets, exit status, start/end UTC и bundle hashes в частном каталоге.
5. Сопоставляет findings с ожидаемыми; проверяет trace разрешённых API, контроль объектов/ACL/GPO/CA до и после. Случайный сетевой audit event не считается изменением конфигурации.
6. Повторяет с revoked read permission, unreachable source, invalid certificate, pagination, membership cycle и частичной policy visibility; не ослабляет TLS или ACL ради прохождения.
7. После отдельного recovery drill владелец recovery предоставляет подписанное свидетельство и дату; аудитор не запускает backup/restore. Drill выполняется в disposable clone по утверждённому runbook.
8. Удаляет временные данные по retention, откатывает только стенд. Evidence summary может быть опубликован лишь после ручного review и удаления инфраструктурных идентификаторов.

## Протокол результата

Для каждого T0-01…REC-01: scenario, rule version, OS/module versions, ожидаемый и фактический status, coverage, private evidence reference, reviewer, дата. Отдельно outcome теста (passed/failed/not_run) и finding status. Failed assertion — провал теста, ожидаемый fail finding в рискованном сценарии может означать passed тест. Skipped не становится passed.

Текущий статус всех Windows сценариев: **not_run**. Стенд не предоставлен и collector не реализован. Public CI никогда не запускает сценарии на private self-hosted runner из pull request. Автоматизация Windows integration будет отдельной задачей после реализации и безопасной настройки закрытого runner.

## Offline MVP: ручное получение и независимая проверка facts

Native collector в v0.1.0a1 не поставляется. Оператор на MGMT1 сначала подготавливает JSON по [контракту](input-contract.md), с synthetic=false, source=manual-lab-review и временем UTC. На старте все checks state=not_run, coverage=none, facts/refs пустые. После подтверждения конкретного источника добавляет ограниченное evidence description с private evidence ID. Эти данные **не отправляются в публичный GitHub или cloud workspace**.

Примеры только чтения для isolated lab; заменить scope на утверждённый lab DC и не считать один ответ полным покрытием. Выполнять локально на соответствующем стендовом host либо через уже утверждённый management path. Нет автоматической выдачи дополнительных прав.

```powershell
# На MGMT1 с RSAT; metadata only, без managed passwords.
Import-Module ActiveDirectory
Get-ADGroupMember -Identity 'Domain Admins' -Server 'dc1.lab.example.test'
Get-ADUser -LDAPFilter '(servicePrincipalName=*)' -Server 'dc1.lab.example.test' -Properties ServicePrincipalName,Enabled,PasswordLastSet |
    Select-Object Name,Enabled,PasswordLastSet,ServicePrincipalName
# На DC: configured registry values, НЕ доказательство effective client behavior.
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\NTDS\Parameters' -Name LDAPServerIntegrity,LdapEnforceChannelBinding
# На каждом scoped SMB server:
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature,EnableSMB1Protocol
```

Эти отдельные команды не вычисляют весь Tier 0 graph, effective ACL или AD CS risk. Членство требует nested/cross-domain review; ACL — ACE/GUID/inheritance/trust review независимым администратором; AD CS — сверку опубликованных templates с CA, enrollment rights, subject flags, EKU, approvals/signatures и control ACL. Пока эти условия не выяснены, оставлять отсутствующие facts или partial coverage. Проверка registry alone не даёт effective LDAP=true. observed_ntlm=false требует определённого окна, всех scoped источников и полноты доставки; отсутствие результата ограниченного event query недостаточно. Lifecycle/stale thresholds утверждаются владельцем перед подсчётом. retention_days подтверждается фактической доступностью данных, а не только configured size.

После независимой сверки каждого fact: `python -m ad_opsec_auditor validate private-snapshot.json`, затем `python -m ad_opsec_auditor audit private-snapshot.json --format json --output private-report.json`. Использовать Python 3.12 в частной лаборатории и полный путь к новому output вне checkout. Данные safe/risky/unavailable сценария подготовить изменениями lab admin; результаты compare с ожидаемым baseline. Отозванное read permission не должно преобразоваться в zero/false. Проверить error exit 2 на повреждённом JSON, unknown на partial coverage и not_run для отсутствующего check.

Протокол приёмки: command/version, SHA256 input, actual exit, expected result каждого check, private evidence refs, independent reviewer и timestamp. Отдельно отмечать отсутствие native collection/safety/compatibility тестов. Даже успешный manual offline run не подтверждает ещё не реализованный collector. Recovery drill подтверждается владельцем в отдельном disposable стенде по утверждённому runbook; никаких восстановлений самим CLI.
