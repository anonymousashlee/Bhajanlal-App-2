#!/usr/bin/env python3
"""Generate the 100 Offensive Security & Penetration Testing OpenCode skills.

Writes SKILL.md instruction files into the global OpenCode skill library and
the project-local skill trees so they are discoverable everywhere.
"""
from pathlib import Path

DATA = """
subdomain-enum-orchestrator|Chain Subfinder, Amass, and puredns to discover and resolve target subdomains.
certificate-transparency-miner|Query crt.sh and Censys logs to uncover historical hostnames and internal domains.
asn-cidr-mapper|Map organization Autonomous System Numbers (ASNs) to IP ranges using BGP databases.
tech-stack-fingerprinter|Identify web servers, frameworks, CDNs, and WAFs using Wappalyzer and HTTP header analysis.
wayback-url-harvester|Extract archived endpoints, parameters, and legacy files from Wayback Machine and Common Crawl.
github-dork-secret-scanner|Search public repositories for exposed API keys, .env files, and hardcoded tokens.
s3-blob-bucket-finder|Enumerate misconfigured AWS S3, Azure Blob, and GCP Storage buckets tied to target domains.
dns-zone-transfer-auditor|Test authoritative name servers for misconfigured AXFR zone transfers and dangling CNAMEs.
shodan-censys-query-builder|Construct targeted queries to find exposed services, self-signed certs, and default banners.
whois-registrar-correlator|Pivot across WHOIS records, registrant emails, and name servers to map corporate acquisitions.
js-bundle-endpoint-extractor|Parse minified JavaScript bundles with LinkFinder to extract hidden API routes.
email-spf-dmarc-auditor|Analyze SPF, DKIM, and DMARC DNS records to assess domain spoofing resilience.
metadata-document-extractor|Run ExifTool on public PDFs and Office docs to identify internal usernames and software versions.
favicon-hash-pivoter|Calculate MurmurHash3 values of favicons to locate origin servers behind CDNs.
virtual-host-fuzzer|Fuzz Host headers against target IP addresses to discover unlinked internal virtual hosts.
nmap-staged-scanner|Run fast SYN port discovery followed by targeted service version and NSE script enumeration.
masscan-highspeed-sweeper|Perform asynchronous TCP/UDP port sweeps across authorized large CIDR blocks.
smb-null-session-enumerator|Check Windows/Samba hosts for anonymous share access, RPC endpoints, and SMB signing status.
snmp-community-walker|Query SNMPv1/v2c services for system info, routing tables, and running processes.
ldap-anonymous-bind-tester|Inspect exposed LDAP directories for unauthenticated base DN and user object queries.
tls-cipher-suite-auditor|Use testssl.sh to flag weak ciphers, expired certificates, and TLS downgrade vulnerabilities.
ike-vpn-aggressive-mode-scanner|Identify IPsec VPN endpoints vulnerable to aggressive-mode PSK hash capture.
nfs-export-permission-checker|Enumerate exported NFS shares and verify no_root_squash misconfigurations.
rdp-vnc-security-inspector|Check remote desktop services for NLA enforcement, encryption levels, and unauthenticated VNC.
smtp-open-relay-verifier|Safely test mail servers for open relay behavior and VRFY/EXPN user enumeration.
ntp-monlist-amplification-check|Audit NTP daemons for exposed mode 6/7 queries and clock-sync misconfigurations.
ipv6-neighbor-discovery-mapper|Enumerate link-local IPv6 hosts and SLAAC addresses on local network segments.
firewall-egress-filter-tester|Determine which outbound ports and protocols are permitted from an internal foothold.
ffuf-directory-param-fuzzer|Fuzz hidden directories, backup files (.bak, .swp), and GET/POST parameters.
nuclei-template-runner|Execute targeted Nuclei YAML templates filtered by detected technology tags and severity.
sqli-error-boolean-prober|Test input vectors for error-based, boolean-blind, and time-based SQL injection.
xss-context-payload-generator|Craft context-aware Cross-Site Scripting payloads for HTML, attribute, and DOM sinks.
ssrf-oob-callback-tester|Test URL-fetching parameters with Interactsh/Burp Collaborator out-of-band callbacks.
idor-access-matrix-verifier|Compare HTTP responses across multi-role session tokens to detect Broken Object Level Auth.
jwt-token-tamper-auditor|Inspect JSON Web Tokens for alg:none, weak HMAC secrets, and kid path traversal.
csrf-samesite-analyzer|Audit state-changing endpoints for missing anti-CSRF tokens and permissive SameSite cookies.
cors-misconfig-checker|Test Origin reflection, null-origin trust, and wildcard credential headers.
xxe-entity-injection-prober|Test XML parsers and SOAP/SVG uploads for external entity resolution and DTD retrieval.
ssti-template-engine-fingerprinter|Identify Jinja2, Twig, Freemarker, or ERB template injection using mathematical probes.
lfi-path-traversal-fuzzer|Test file parameters for directory traversal (../) and PHP/Java stream wrapper exposure.
file-upload-filter-bypasser|Audit upload handlers for MIME-type mismatches, polyglot files, and double extensions.
http-request-smuggling-tester|Probe frontend/backend proxy chains for CL.TE and TE.CL desynchronization.
graphql-introspection-auditor|Check GraphQL endpoints for enabled introspection, batching abuse, and depth limits.
oauth-redirect-uri-validator|Test OAuth/OIDC authorization flows for open redirect_uri bypasses and missing state params.
web-cache-poisoning-prober|Test unkeyed headers (X-Forwarded-Host) to see if malicious responses persist in cache.
race-condition-turbo-sender|Send synchronized concurrent HTTP/2 requests to test coupon, balance, or limit race conditions.
websocket-message-interceptor|Fuzz WebSocket frames for missing authorization checks and cross-site WebSocket hijacking.
subdomain-takeover-verifier|Match dangling DNS records against known unclaimed cloud service fingerprints.
bloodhound-collector-runner|Gather AD domain relationships, ACLs, and session data using SharpHound or BloodHound.py.
kerberoasting-spn-extractor|Enumerate user accounts with Service Principal Names (SPNs) for offline TGS ticket auditing.
asreproasting-preauth-scanner|Identify AD accounts with Kerberos pre-authentication disabled.
adcs-template-misconfig-auditor|Run Certipy to identify vulnerable Active Directory Certificate Services templates (ESC1-ESC8).
smb-relay-target-identifier|Build lists of domain hosts with SMB signing disabled for relay risk assessment.
gpo-password-permission-auditor|Inspect Group Policy Objects for weak folder ACLs and legacy cpassword attributes.
bloodhound-cypher-path-querier|Query Neo4j databases for shortest attack paths from compromised users to Domain Admins.
ntlm-hash-password-policy-auditor|Cross-check authorized NTDS.dit dumps against password dictionaries for compliance audits.
kerberos-delegation-auditor|Identify hosts configured with Unconstrained or Constrained Delegation permissions.
laps-read-permission-checker|Audit which groups can read Local Administrator Password Solution (LAPS) attributes.
responder-llmnr-nbtns-auditor|Assess broadcast name-resolution exposure (LLMNR/NBT-NS/mDNS) on internal subnets.
acl-genericall-writeowner-mapper|Flag non-admin accounts holding GenericAll, WriteDacl, or WriteOwner over privileged objects.
linpeas-winpeas-output-parser|Summarize privilege escalation enumeration logs into prioritized actionable findings.
linux-suid-capabilities-auditor|Cross-reference SUID binaries and Linux file capabilities against GTFOBins.
sudoers-wildcard-injection-checker|Analyze sudo -l rules for NOPASSWD entries, LD_PRELOAD, and wildcard arguments.
cron-systemd-writable-scanner|Detect scheduled tasks or systemd unit files writable by unprivileged users.
windows-unquoted-service-path-finder|Identify Windows services with unquoted binary paths containing spaces and writable directories.
alwaysinstallelevated-registry-checker|Query Windows registry keys for MSI elevated installation misconfigurations.
ssh-key-agent-forwarding-auditor|Locate exposed private keys, authorized_keys, and active SSH_AUTH_SOCK sockets.
windows-token-privilege-inspector|Check whoami /priv for SeImpersonatePrivilege or SeBackupPrivilege.
container-escape-capability-checker|Inspect Docker/Podman containers for --privileged, CAP_SYS_ADMIN, or mounted docker.sock.
kernel-exploit-suggester|Match OS kernel versions and patch levels against known local privilege escalation CVEs.
aws-iam-policy-privesc-analyzer|Parse IAM JSON policies to identify privilege escalation paths (e.g., iam:PassRole).
imds-v1-ssrf-exposure-checker|Verify EC2/GCP/Azure instances enforce IMDSv2 session tokens against metadata SSRF.
prowler-scoutsuite-runner|Orchestrate automated cloud security posture audits across AWS, Azure, and GCP accounts.
kubernetes-rbac-permission-auditor|Analyze ClusterRoles and RoleBindings for over-privileged pods/exec or secrets access.
kubelet-anonymous-port-scanner|Check Kubernetes worker nodes for unauthenticated port 10250 Kubelet APIs.
helm-terraform-iac-scanner|Run Checkov or tfsec on Infrastructure-as-Code templates before cloud deployment.
docker-image-layer-secret-extractor|Inspect container image history and tar layers for deleted secrets and credentials.
ecr-acr-registry-public-auditor|Check container registries for anonymous pull permissions or unpatched base images.
lambda-serverless-env-auditor|Review serverless function configurations for plaintext secrets and overly broad execution roles.
k8s-network-policy-gap-finder|Identify namespaces lacking ingress/egress NetworkPolicy isolation.
ghidra-headless-decompiler|Run Ghidra scripts to export decompiled C pseudocode and function call graphs.
strings-entropy-packer-detector|Analyze binary sections for high Shannon entropy, UPX packing, and embedded URLs.
checksec-binary-mitigation-auditor|Inspect ELF/PE binaries for NX, ASLR/PIE, Stack Canaries, and RELRO protections.
gdb-pwndbg-crash-triager|Automate crash input minimization and register state inspection during fuzzing triage.
afl-libfuzzer-harness-builder|Generate fuzzing harnesses for C/C++/Rust parser functions to uncover memory corruption.
apk-jadx-manifest-auditor|Decompile Android APKs and flag android:debuggable="true" and exported components.
frida-ssl-pinning-hooker|Write Frida JS instrumentation scripts to inspect encrypted mobile API traffic during audits.
ios-ipa-plist-keychain-inspector|Analyze iOS Info.plist URL schemes, ATS exceptions, and binary entitlements.
firmware-binwalk-filesystem-extractor|Unpack embedded IoT firmware images to audit /etc/shadow, web servers, and hard-coded keys.
uart-jtag-pinout-identifier|Analyze PCB documentation and logic analyzer captures to identify debug interfaces.
semgrep-custom-rule-writer|Author custom Semgrep AST rules to detect insecure sinks across Python, Go, JS, and Java.
codeql-taint-tracking-querier|Write CodeQL queries tracing untrusted user input from sources to SQL/command sinks.
dependency-cve-sbom-scanner|Generate CycloneDX SBOMs and scan lockfiles with Trivy/Grype for vulnerable libraries.
deserialization-gadget-auditor|Audit Java, PHP, Python (pickle), and .NET codebases for unsafe object deserialization.
wpa2-pmkid-handshake-auditor|Capture and audit authorized Wi-Fi 4-way handshakes and PMKIDs with hcxdumptool/Hashcat.
ble-gatt-characteristic-enumerator|Scan Bluetooth Low Energy peripherals for unauthenticated read/write GATT characteristics.
cvss-v4-severity-calculator|Compute accurate CVSS v3.1 and v4.0 base vectors and environmental scores for findings.
pentest-finding-report-formatter|Transform raw tool logs and PoC requests into structured executive and technical report sections.
remediation-patch-verifier|Generate minimal code diffs and unit tests to verify security fixes close reported bugs.
scope-guardrail-validator|Cross-check target IPs and domains against authorized rules-of-engagement allowlists before running tools.
"""

GROUPS = [
    (113, "Reconnaissance & OSINT", 15, 1, 15),
    (114, "Network & Infrastructure Scanning", 13, 16, 28),
    (115, "Web Application Vulnerability Testing", 20, 29, 48),
    (116, "Active Directory & Windows Security", 12, 49, 60),
    (117, "Privilege Escalation & Post-Exploitation", 10, 61, 70),
    (118, "Cloud, Containers & Kubernetes Security", 10, 71, 80),
    (119, "Reverse Engineering, Binary & Mobile Analysis", 10, 81, 90),
    (120, "Source Code Audit, Wireless & Reporting", 10, 91, 100),
]

ACRONYMS = {
    "Asn": "ASN", "Cidr": "CIDR", "Dns": "DNS", "Ssh": "SSH", "Tls": "TLS",
    "Http": "HTTP", "Https": "HTTPS", "Jwt": "JWT", "Xss": "XSS", "Sqli": "SQLi",
    "Ssrf": "SSRF", "Idor": "IDOR", "Csrf": "CSRF", "Cors": "CORS", "Xxe": "XXE",
    "Ssti": "SSTI", "Lfi": "LFI", "Api": "API", "Url": "URL", "Ip": "IP",
    "Ipv6": "IPv6", "Smb": "SMB", "Snmp": "SNMP", "Ldap": "LDAP", "Nfs": "NFS",
    "Rdp": "RDP", "Vnc": "VNC", "Smtp": "SMTP", "Ntp": "NTP", "Spn": "SPN",
    "Adcs": "ADCS", "Gpo": "GPO", "Laps": "LAPS", "Acl": "ACL", "Suid": "SUID",
    "Msi": "MSI", "Aws": "AWS", "Gcp": "GCP", "Spf": "SPF", "Dmarc": "DMARC",
    "Dkim": "DKIM", "Cname": "CNAME", "Axfr": "AXFR", "Html": "HTML", "Dom": "DOM",
    "Cdn": "CDN", "Waf": "WAF", "S3": "S3", "Js": "JS", "Elf": "ELF", "Pe": "PE",
    "Apk": "APK", "Ipa": "IPA", "Ble": "BLE", "Gatt": "GATT", "Sbom": "SBOM",
    "Cve": "CVE", "Wpa": "WPA", "Pmkid": "PMKID", "Oauth": "OAuth", "Oidc": "OIDC",
    "Graphql": "GraphQL", "Vrfy": "VRFY", "Ntds": "NTDS", "Llmnr": "LLMNR",
    "Ike": "IKE", "Psk": "PSK", "Rce": "RCE", "Cli": "CLI",
}

ROOTS = [
    Path.home() / ".config/opencode/skills",
    Path("/Users/ashleesharma/Bhajanlal-App 2/.opencode/skills"),
    Path("/Users/ashleesharma/gods-eye-view/.opencode/skills"),
    Path("/Users/ashleesharma/gods-eye-view/.agents/skills"),
]


def title_for(skill_id: str) -> str:
    words = skill_id.replace("-", " ").title().split()
    return " ".join(ACRONYMS.get(w, w) for w in words)


def render(idx: int, skill_id: str, desc: str, pillar: int, ptitle: str, count: int) -> str:
    name = title_for(skill_id)
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {desc}\n"
        "---\n\n"
        f"# {name}\n\n"
        "Part of the **Bhajanlal** OpenCode skill library.\n\n"
        f"Pillar: {pillar}. {ptitle} ({count} skills)\n\n"
        "Use only on systems you own or have explicit written authorization to test.\n\n"
        "## Workflow\n\n"
        "1. Confirm written authorization and the exact in-scope targets before running any tool.\n"
        f"2. Prepare the tooling described here ({desc.rstrip('.')}) and set scoped, rate-limited parameters.\n"
        "3. Execute against authorized targets only, capturing raw output and timestamps.\n"
        "4. Correlate results with other findings and manually validate every candidate issue.\n"
        "5. Record evidence, assign severity, and map each finding to a concrete remediation.\n\n"
        "## Output\n\n"
        "A structured finding set with evidence, confidence, severity, and remediation guidance, "
        "plus a short executive summary suitable for a rules-of-engagement report.\n"
    )


def main() -> None:
    rows = [tuple(line.split("|", 1)) for line in DATA.strip().splitlines()]
    assert len(rows) == 100, len(rows)
    written = 0
    for pillar, ptitle, count, start, end in GROUPS:
        for offset, (skill_id, desc) in enumerate(rows[start - 1:end], start=1):
            content = render(offset, skill_id, desc, pillar, ptitle, count)
            for root in ROOTS:
                target = root / skill_id / "SKILL.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            written += 1
    print(f"Wrote {written} offensive-security skills to {len(ROOTS)} skill trees")


if __name__ == "__main__":
    main()
