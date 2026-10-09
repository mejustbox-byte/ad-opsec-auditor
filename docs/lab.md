# Изолированный Windows-стенд и ручная приёмка

## Топология

Отдельная сеть без production маршрутов; lab.example.test. DC1/DC2 Windows Server 2022 AD DS/DNS, отдельный CA1 с корпоративным AD CS, MEMBER1 для SMB/сервисов, MGMT1 с PowerShell 5.1 и RSAT ActiveDirectory/GroupPolicy. Второй домен/доверие добавляется после базовых сценариев. 2019/2025 проверяются отдельно, поддержка не заявляется. Образы/лицензии предоставляет владелец, не облачная задача.

Планировать 5 VM по 2 vCPU/4 GiB и диск от 60 GiB, затем уточнить нагрузкой. DNS/время обязательны. Разрешены только утверждённые лабораторные узлы; порты не публикуются в Интернет, WinRM автоматически не открывается. Проверки сертификатов/подписи не отключаются.

## Роли и данные

Администратор отдельно создаёт конфигурации и контрольные точки. AuditReader — отдельная непривилегированная запись с конкретными read-разрешениями. Domain Admin не использовать как обход отказа. Credentials вводятся средствами Windows, не Git/чатом/аргументом CLI. Даже тестовые секреты не коммитятся.

Вымышленные группы Tier0-Lab, svc-demo и LabTemplate создаются только здесь. Реальные выгрузки остаются в частном каталоге с ACL/шифрованием, без Actions. Публичные примеры создаются вручную, не копированием exports. Срок хранения исходно 7 дней либо иной согласованный владельцем.

## Будущая проверка сборщика

1. Зафиксировать владельца, область, версии ОС/модулей, контрольную точку до сценария.
2. Администратор создаёт безопасный, рискованный и недоступный вариант каждой проверки; аудитор ничего не меняет.
3. Оператор фиксирует SID и минимальные права; отказ доступа должен дать unknown, без повышения прав.
4. Будущий сбор ограничен бюджетом/временем; private metadata журнала, exit, UTC и hashes сохраняются без secrets.
5. Сверить ожидаемые результаты и трассу разрешённых API, сравнить AD/ACL/GPO/CA до и после. Сетевое audit событие не равно изменению конфигурации.
6. Проверить denied/unreachable/invalid certificate, страницы, циклы групп и частичную видимость. Не ослаблять TLS/права ради прохождения.
7. Recovery owner отдельно выполняет разрешённое учение в изолированном клоне; аудитор только фиксирует датированное свидетельство, не запускает restore.
8. Удалить временные данные по сроку и откатить только стенд. Публично допустима лишь вручную проверенная сводка без идентификаторов инфраструктуры.

## Ручной ввод для автономного MVP

Сборщик отсутствует. На MGMT1 оператор создаёт JSON по [контракту](input-contract.md): synthetic=false, source=manual-lab-review, UTC. Изначально наблюдения not_run/none с пустыми facts/refs; после независимой проверки источника — соответствующие факты и private evidence ID. Данные не отправлять в этот cloud/public Git.

Примеры только чтения; один ответ не доказывает полного покрытия всех узлов:

```powershell
Import-Module ActiveDirectory
Get-ADGroupMember -Identity 'Domain Admins' -Server 'dc1.lab.example.test'
Get-ADUser -LDAPFilter '(servicePrincipalName=*)' -Server 'dc1.lab.example.test' -Properties ServicePrincipalName,Enabled,PasswordLastSet |
    Select-Object Name,Enabled,PasswordLastSet,ServicePrincipalName
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\NTDS\Parameters' -Name LDAPServerIntegrity,LdapEnforceChannelBinding
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature,EnableSMB1Protocol
```

Членство требует вложенных/междоменных проверок; ACL — независимой проверки порядка/наследования/GUID/доверий; AD CS — опубликованных шаблонов, CA, прав выдачи, EKU/субъекта/одобрения/подписей и ACL управления. Registry alone не даёт effective LDAP=true. observed_ntlm=false требует полного согласованного окна/источников, не пустой ограниченной выборки. Пороги устаревания утверждает владелец; retention_days подтверждает фактические данные, не только размер настройки.

После независимой сверки: `python -m ad_opsec_auditor validate private-snapshot.json`, затем `python -m ad_opsec_auditor audit private-snapshot.json --format json --output private-report.json`. Python 3.12 в частной среде, output вне checkout и новое имя. Частичное покрытие должно дать unknown, отсутствующая проверка — not_run, повреждённый JSON — exit 2. Safe/risky outcome сверить с [матрицей](check-matrix.md).

Протокол: версии/команда, SHA256 входа, scope, expected/actual для каждой проверки, фактический exit, private evidence refs, независимый reviewer и UTC. Expected fail finding может означать успешный рискованный тест; skipped не passed. **Все реальные сценарии пока not_run / НЕ ВЫПОЛНЕНО**. Успешный manual offline run не подтверждает ещё не реализованный сборщик. [Локальный ПК](../LOCAL-PC.md).
