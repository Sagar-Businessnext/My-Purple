# Bandit B-Codes Reference

## How to Read Bandit Output

```
>> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection via string-based query construction.
   Severity: Medium   Confidence: Medium
   CWE: CWE-89 (https://cwe.mitre.org/data/definitions/89.html)
   Location: src/my_service/repositories/user_repo.py:42:20
```

Fields: `[B-code:rule_name]`, Severity (LOW/MEDIUM/HIGH), Confidence (LOW/MEDIUM/HIGH), CWE, file:line:col.

## High-Priority B-Codes (HIGH or common MEDIUM)

| B-Code | Rule Name | Severity | Confidence | Description |
|--------|-----------|----------|------------|-------------|
| B101 | assert_used | LOW | HIGH | `assert` used — disabled by `-O` in production |
| B102 | exec_used | MEDIUM | HIGH | `exec()` call — arbitrary code execution risk |
| B103 | set_bad_file_permissions | MEDIUM | MEDIUM | `os.chmod` setting world-writable permissions |
| B105 | hardcoded_password_string | LOW | MEDIUM | String assigned to variable named `password`, `passwd`, `pwd` |
| B106 | hardcoded_password_funcarg | LOW | MEDIUM | String passed as argument named `password` |
| B107 | hardcoded_password_default | LOW | MEDIUM | Default parameter value contains password-like string |
| B108 | hardcoded_tmp_directory | MEDIUM | MEDIUM | Use of `/tmp` or `tmpnam` — predictable temp paths |
| B201 | flask_debug_true | HIGH | HIGH | Flask app with `debug=True` |
| B301 | pickle | MEDIUM | HIGH | `pickle` or `cPickle` used — unsafe deserialization |
| B302 | marshal | MEDIUM | HIGH | `marshal.loads()` — unsafe deserialization |
| B303 | md5 | MEDIUM | HIGH | `hashlib.md5` or `MD5` — weak hash for sensitive data |
| B304 | ciphers | HIGH | HIGH | Insecure cipher algorithm (DES, RC4, Blowfish) |
| B305 | cipher_modes | MEDIUM | HIGH | Insecure cipher mode (ECB) |
| B306 | mktemp_q | MEDIUM | HIGH | `tempfile.mktemp` — race condition in temp file creation |
| B307 | eval | HIGH | HIGH | `eval()` used |
| B311 | random | LOW | HIGH | `random` module used for security/cryptographic purpose |
| B320 | xml_bad_expatbuilder | MEDIUM | HIGH | Vulnerable XML parser (XXE risk) |
| B401 | import_telnetlib | HIGH | HIGH | `telnetlib` imported — plaintext protocol |
| B501 | request_with_no_cert_validation | HIGH | HIGH | TLS cert verification disabled (`verify=False`) |
| B502 | ssl_with_bad_version | HIGH | HIGH | Old SSL/TLS version specified |
| B506 | yaml_load | MEDIUM | HIGH | `yaml.load()` without `Loader=yaml.SafeLoader` |
| B601 | paramiko_calls | MEDIUM | HIGH | `paramiko` exec_command — shell injection risk |
| B602 | subprocess_popen_with_shell_equals_true | HIGH | HIGH | `subprocess` with `shell=True` |
| B603 | subprocess_without_shell_equals_true | LOW | HIGH | `subprocess` without shell — lower risk but log |
| B604 | any_other_function_with_shell_equals_true | MEDIUM | LOW | Function call with `shell=True` |
| B605 | start_process_with_a_shell | HIGH | HIGH | `os.system()` or `os.popen()` call |
| B606 | start_process_with_no_shell | LOW | MEDIUM | `os.execl`, `os.execle`, `os.execlp` |
| B607 | start_process_with_partial_path | LOW | HIGH | Process started with partial path (PATH injection risk) |
| B608 | hardcoded_sql_expressions | MEDIUM | MEDIUM | String-formatted SQL query |
| B701 | jinja2_autoescape_false | HIGH | HIGH | Jinja2 `autoescape=False` — XSS risk |
| B703 | django_mark_safe | MEDIUM | HIGH | `mark_safe()` in Django — XSS if input is uncontrolled |

## Severity × Confidence Decision Matrix

| Severity / Confidence | HIGH | MEDIUM | LOW |
|-----------------------|------|--------|-----|
| **HIGH** | Blocker — fix immediately | Blocker — investigate and fix | Blocker — investigate; may suppress with justification |
| **MEDIUM** | Required fix | Required fix | Review; fix or suppress with justification |
| **LOW** | Informational — review | Informational — skip if context is clear | Usually skip |

## Common False Positives

| B-Code | Scenario | Ruling |
|--------|----------|--------|
| B101 (assert) | `assert isinstance(x, int)` in type narrowing within test files | Suppress in `tests/` — acceptable |
| B303 (md5) | `hashlib.md5(content.encode()).hexdigest()` used as a non-security cache key or ETag | Suppress if there is a comment confirming it is not used for security |
| B311 (random) | `random.choice(sample_data)` in test fixtures | Suppress in test files |
| B603 (subprocess) | `subprocess.run(["git", "status"])` with static argument list | LOW severity; review and suppress with comment |
| B608 (sql) | SQLAlchemy query with a hardcoded string that is not user-controlled | Investigate; suppress only if query string is fully static |
