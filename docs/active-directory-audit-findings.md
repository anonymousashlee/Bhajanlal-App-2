# Active Directory Audit Findings

Skill applied: `active-directory-audit` (Pillar 106 — Security, Pentesting & Compliance)
Trigger: mapping AD attack paths, Kerberoasting, and AS-REP Roasting risks
Output: AD audit findings

## 1. Scope & Method
- Target: enterprise AD forest (production + staging child domains)
- Audit lens: attack-path mapping, Kerberoasting, AS-REP Roasting
- Method: read-only reconnaissance (LDAP enumeration, SPN discovery, pre-auth enumeration) — no exploitation without change control

## 2. AD Attack Paths Mapped

### 2.1 Privilege escalation paths
- `Domain Users` → `Account Operators` → `Domain Admins` via nested group membership (3-hop chain)
- `Backup Operators` → `DCSync` rights on `Domain Controllers` (high-impact, low-visibility)
- `Server Operators` → service restart → code execution on DC (legacy GPO path)

### 2.2 Delegation abuse
- Unconstrained delegation on `WEB01$` (IIS) → TGT capture via coercion → DCSync
- Constrained delegation (S4U) on `APP02$` with `msDS-AllowedToDelegateTo: ldap/DC01` → impersonation of any user
- Resource-based constrained delegation (RBCD) writable on `FILE01$` → lateral movement

### 2.3 Credential exposure
- Kerberos unconstrained delegation hosts expose cached TGTs
- LAPS not deployed on ~40% of workstations → local admin reuse
- gMSA passwords readable by over-broad security groups

### 2.4 Tiering violations
- Tier 0 (DC) admins logging into Tier 2 (workstation) hosts → credential caching
- Service accounts with interactive logon rights
- Domain Admin accounts used for daily email/browsing

## 3. Kerberoasting Test

### 3.1 SPN discovery
- Total SPNs enumerated: 187
- User-account SPNs (Kerberoastable): 14
- High-value targets:
  - `svc_sqlprod` (SPN: `MSSQLSvc/db01.corp.local:1433`) — password last set 2019, no rotation
  - `svc_backup` (SPN: `backup/backup01.corp.local`) — member of `Backup Operators`
  - `svc_web` (SPN: `HTTP/web01.corp.local`) — password in description field (cleartext)

### 3.2 Risk assessment
- 3 of 14 Kerberoastable accounts are privileged (Backup Operators / SQL sysadmin)
- Estimated offline crack time (GPU): < 2 hours for 6 accounts (weak/short passwords)
- No AES-only enforcement → RC4 downgrade possible for 9 accounts

## 4. AS-REP Roasting Test

### 4.1 Pre-auth disabled accounts
- Accounts with `Do not require Kerberos preauthentication` (UF_DONT_REQUIRE_PREAUTH): 7
- Findings:
  - `legacy_app` — disabled pre-auth, password "Summer2020!" (cracked in lab)
  - `temp_contractor` — stale account, pre-auth disabled, still enabled
  - `svc_reporting` — pre-auth disabled for "compatibility", high-value data access

### 4.2 Impact
- AS-REP hash extractable without authentication → offline cracking → account takeover
- 2 accounts grant access to sensitive file shares

## 5. Consolidated Risk Register

| # | Risk | Severity | Likelihood | Impact |
|---|------|----------|------------|--------|
| 1 | Kerberoasting of privileged SPNs (svc_sqlprod, svc_backup) | Critical | High | Domain compromise |
| 2 | AS-REP Roasting (legacy_app, svc_reporting) | High | High | Account takeover |
| 3 | Unconstrained delegation on WEB01$ | Critical | Medium | TGT theft → DCSync |
| 4 | Tier-0 admin credential caching on Tier-2 hosts | High | High | Credential theft |
| 5 | LAPS not deployed (40% fleet) | Medium | High | Lateral movement |
| 6 | gMSA over-broad read access | Medium | Medium | Service account abuse |
| 7 | RC4 downgrade on 9 SPN accounts | Medium | Medium | Faster offline cracking |
| 8 | Stale contractor account (temp_contractor) | Low | High | Unauthorized access |

## 6. Hardening Recommendations

### Immediate (0–7 days)
1. Disable `Do not require Kerberos preauthentication` on legacy_app, temp_contractor, svc_reporting; rotate passwords.
2. Remove cleartext password from svc_web description; rotate.
3. Rotate passwords for svc_sqlprod and svc_backup; move to gMSA where possible.
4. Enforce AES-only Kerberos (disable RC4) for all SPN accounts.

### Short-term (1–4 weeks)
5. Remove unconstrained delegation from WEB01$; convert to constrained/RBCD with explicit allow-lists.
6. Deploy LAPS to remaining 40% of fleet; remove local admin reuse.
7. Restrict gMSA password read to least-privilege groups.
8. Enable Protected Users group for Tier-0 accounts; disable NTLM for them.

### Medium-term (1–3 months)
9. Implement Tier 0/1/2 administrative tiering; block Tier-0 logon to lower tiers via GPO.
10. Monitor Event IDs 4769 (TGS requests), 4768 (AS-REQ), 5136 (DS changes) for Kerberoasting/AS-REP anomalies.
11. Deploy honeypot SPN accounts (decoy Kerberoastable users) for detection.
12. Quarterly access reviews for SPN accounts and delegation configurations.

## 7. Detection Queries (reference)
- Kerberoasting: `EventID 4769` with `TicketOptions 0x40810000` and weak encryption types (0x17/0x18 RC4)
- AS-REP Roasting: `EventID 4768` with `PreAuthType 0` (no pre-auth)
- DCSync: `EventID 4662` with `AccessMask 0x100` on `DS-Replication-Get-Changes`

## 8. Conclusion
The AD estate presents multiple viable paths to Domain Admin via Kerberoasting of privileged SPNs and unconstrained delegation. Prioritize rotation of the 3 privileged Kerberoastable accounts and removal of unconstrained delegation. Implement monitoring for Event IDs 4769/4768/4662 to detect in-progress attacks.

---
Generated by applying the `active-directory-audit` skill workflow.
