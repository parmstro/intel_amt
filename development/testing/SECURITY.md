# Security Guidelines for parmstro.intel_amt Collection

## CRITICAL: Never Commit Passwords

**NEVER** hardcode passwords in:
- ❌ Playbooks
- ❌ Test files
- ❌ Debug scripts
- ❌ Documentation examples
- ❌ Any code or configuration files

## Proper Credential Management

### Use Ansible Vault

**ALWAYS** use Ansible Vault for sensitive data:

```bash
# Create vault file
ansible-vault create vault.yml

# Add credentials
amt_password: 'your_password_here'
```

### Reference Vaulted Variables

```yaml
# In playbooks
vars_files:
  - vault.yml

tasks:
  - name: Use AMT module
    parmstro.intel_amt.amt_power:
      password: "{{ amt_password }}"  # From vault
```

### Vault Password File

Store vault password securely (NOT in git):

```bash
echo 'your_vault_password' > .vault_password
chmod 600 .vault_password

# Add to .gitignore
echo '.vault_password' >> .gitignore
```

### Using Vaulted Credentials

```bash
# With password file
ansible-playbook playbook.yml --vault-password-file=.vault_password

# Prompt for password
ansible-playbook playbook.yml --ask-vault-pass
```

## Module Security Features

### Password Protection

All modules mark the `password` parameter with `no_log: true` to prevent logging:

```python
password=dict(type='str', required=True, no_log=True)
```

### SSL/TLS

- Default: TLS enabled (`use_tls: true`)
- Self-signed certificates: Set `verify_ssl: false`
- **Never** disable TLS verification on untrusted networks

## Testing Securely

### Test Files Must Use Vault

```yaml
# ❌ WRONG - Hardcoded password
vars:
  amt_password: 'MySecretPassword123'

# ✅ CORRECT - From vault
vars_files:
  - vault/amt_credentials.yml

# Variables use _vault suffix
amt_password: "{{ amt_password_vault }}"
```

### Debug Scripts

- Never commit debug scripts with credentials
- Add to .gitignore:
  ```
  debug_*.py
  test_*.py
  ```

## Pre-Commit Checks

Before committing:

```bash
# Check for password leaks
git diff | grep -i password
git diff | grep -i "Legend\|secret\|pass="

# Ensure vault files are encrypted
file tests/integration/vault.yml
# Should show: "data" (encrypted) not "ASCII text"
```

## AMT Network Security

### Isolate AMT Network

Keep AMT management interfaces on a separate VLAN:

```
Production Network: 192.168.1.0/24
AMT Management:     192.168.254.0/24
```

### Firewall Rules

```bash
# Only allow AMT access from management systems
iptables -A INPUT -p tcp --dport 16992 -s 192.168.1.100 -j ACCEPT
iptables -A INPUT -p tcp --dport 16992 -j DROP
```

### Change Default Passwords

**ALWAYS** change AMT default passwords:
- Access AMT BIOS (Ctrl+P during boot)
- Set strong admin password
- Document in vault file

## Best Practices

### 1. Credential Rotation

Rotate AMT passwords regularly:

```yaml
- name: Update AMT password (future module)
  parmstro.intel_amt.amt_user:
    old_password: "{{ old_amt_password }}"
    new_password: "{{ new_amt_password }}"
```

### 2. Least Privilege

Use dedicated AMT accounts with minimal permissions when possible.

### 3. Audit Logging

Enable and monitor AMT event logs:

```yaml
- name: Retrieve AMT logs
  parmstro.intel_amt.amt_event_log:
    ...
  register: amt_logs
```

### 4. Network Segmentation

- Keep AMT on isolated management network
- Use VPN for remote access
- Never expose AMT to public internet

### 5. Encrypted Transport

Always use HTTPS when possible:

```yaml
parmstro.intel_amt.amt_power:
  use_tls: true
  verify_ssl: true  # Use valid certs
```

## Security Review Checklist

Before publishing or sharing:

- [ ] No passwords in playbooks
- [ ] No passwords in test files
- [ ] No passwords in debug scripts
- [ ] All credentials in vault files
- [ ] Vault files are encrypted
- [ ] .vault_password in .gitignore
- [ ] Debug scripts in .gitignore
- [ ] No secrets in git history
- [ ] SSL verification enabled for production
- [ ] Authentication failures handled gracefully

## Incident Response

If credentials are compromised:

1. **Immediately** change all AMT passwords
2. Rotate vault password
3. Review AMT event logs for unauthorized access
4. Check for unauthorized power operations
5. Update all systems with new credentials
6. Review git history for exposure

## Reporting Security Issues

Report security vulnerabilities to:
- GitHub: https://github.com/parmstro/intel_amt/security/advisories
- **Do not** open public issues for security vulnerabilities

## Compliance

This collection follows:
- Ansible security best practices
- NIST guidelines for out-of-band management
- Industry standards for credential management

## Additional Resources

- [Ansible Vault Documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
- [Intel AMT Security Best Practices](https://software.intel.com/content/www/us/en/develop/articles/intel-amt-security-features.html)
- [CIS Benchmarks for Network Devices](https://www.cisecurity.org/)
