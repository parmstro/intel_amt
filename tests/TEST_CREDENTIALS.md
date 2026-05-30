# Test Credential Management

This document describes professional approaches for handling credentials in tests.

## Overview

**NEVER commit passwords or secrets to the repository.**

This collection uses a **vault directory** pattern as the standard practice, with environment variable support for CI/CD.

## 1. Vault Directory (Standard Practice)

The standard practice for local testing and shared development environments.

### Setup

```bash
# 1. Create vault password file
echo 'your_vault_password' > .vault_password
chmod 600 .vault_password

# 2. Create encrypted credentials in vault directory
ansible-vault create vault/test_credentials.yml --vault-password-file=.vault_password

# Add credentials (use _vault suffix):
---
amt_password_vault: 'YourTestPasswordHere'
amt_username_vault: 'admin'
```

### Usage in Playbooks

All test playbooks automatically load vault files:

```yaml
tasks:
  - name: Load vaulted credentials
    ansible.builtin.include_vars:
      dir: vault
      ignore_unknown_extensions: true
      extensions:
        - yml
        - yaml
    no_log: true
```

### Running Tests

```bash
# With password file (recommended)
ansible-playbook test_log_lifecycle.yml --vault-password-file=.vault_password

# Interactive password prompt
ansible-playbook test_log_lifecycle.yml --ask-vault-pass

# Integration tests
make integration VAULT_PASSWORD_FILE=.vault_password
```

### Editing Vault Files

```bash
# Edit existing vault file
ansible-vault edit vault/test_credentials.yml --vault-password-file=.vault_password

# View vault file (read-only)
ansible-vault view vault/test_credentials.yml --vault-password-file=.vault_password

# Rekey vault with new password
ansible-vault rekey vault/test_credentials.yml --vault-password-file=.vault_password
```

## 2. Environment Variables (For CI/CD)

Fallback method for automated testing and CI/CD pipelines where vault files aren't available.

```bash
# Set test credentials as environment variables
export AMT_USERNAME="admin"
export AMT_PASSWORD="YourTestPasswordHere"

# Run tests with environment variable fallback
ansible-playbook test_log_lifecycle.yml \
  -e "amt_username_vault=${AMT_USERNAME}" \
  -e "amt_password_vault=${AMT_PASSWORD}"
```

Playbooks automatically use environment variables when available:

```yaml
vars:
  test_host: "{{ lookup('env', 'AMT_TEST_HOST') | default('c1s2n2.amt.parmstrong.ca') }}"
  test_user: "{{ lookup('env', 'AMT_TEST_USER') | default('admin') }}"
  test_pass: "{{ lookup('env', 'AMT_TEST_PASSWORD') | default(amt_test_password) }}"
```

## 3. Hybrid Approach (Vault + Environment Variables)

The test playbooks use a hybrid approach for maximum flexibility:

```yaml
vars:
  # Try environment variables first
  test_host: "{{ lookup('env', 'AMT_TEST_HOST') | default('c1s2n2.amt.parmstrong.ca') }}"
  test_user: "{{ lookup('env', 'AMT_TEST_USER') | default('admin') }}"

tasks:
  # Load vaulted credentials if available
  - name: Load vaulted credentials
    ansible.builtin.include_vars:
      dir: vault
      ignore_unknown_extensions: true
    no_log: true

  # Use password from environment or vault
  - name: Test module
    parmstro.intel_amt.amt_power:
      password: "{{ lookup('env', 'AMT_TEST_PASSWORD') | default(amt_test_password) }}"
```

This allows:
- **Local development**: Use vault directory (standard practice)
- **CI/CD**: Override with environment variables
- **Flexibility**: Mix and match based on what's available

## 4. Interactive Prompts (For Manual Testing)

```yaml
vars_prompt:
  - name: amt_password
    prompt: "Enter AMT password"
    private: true
```

## 5. External Credential Stores (For Enterprise)

```yaml
# Using HashiCorp Vault
- name: Get AMT credentials
  ansible.builtin.set_fact:
    amt_password: "{{ lookup('hashi_vault', 'secret/amt:password') }}"

# Using AWS Secrets Manager
- name: Get AMT credentials
  amazon.aws.aws_secret:
    name: amt_credentials
  register: amt_secret
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
- name: Run integration tests
  env:
    AMT_TEST_HOST: ${{ secrets.AMT_TEST_HOST }}
    AMT_TEST_PASSWORD: ${{ secrets.AMT_TEST_PASSWORD }}
  run: |
    ansible-playbook tests/integration/targets/amt_power/tasks/main.yml
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  variables:
    AMT_TEST_HOST: $AMT_TEST_HOST  # From CI/CD settings
    AMT_TEST_PASSWORD: $AMT_TEST_PASSWORD
  script:
    - ansible-playbook tests/integration/targets/amt_power/tasks/main.yml
```

## Security Notes

1. **NEVER** commit:
   - `.vault_password` files
   - Unencrypted vault files
   - Scripts with hardcoded passwords
   - Environment variable exports with passwords

2. **ALWAYS**:
   - Use environment variables in CI/CD
   - Use vault directory for local development
   - Keep `.vault_password` out of git
   - Rotate test credentials regularly
   - Use `no_log: true` when loading credentials

3. **Add to .gitignore**:
   ```
   .vault_password
   .vault_pass
   vault_pass.txt
   vault/*.yml
   vault/*.yaml
   ```

## Quick Start for Developers

```bash
# 1. Clone repository
git clone https://github.com/parmstro/intel_amt.git
cd intel_amt

# 2. Create vault password file
echo 'your_vault_password' > .vault_password
chmod 600 .vault_password

# 3. Create vault credentials
ansible-vault create vault/test_credentials.yml --vault-password-file=.vault_password

# 4. Run tests
ansible-playbook test_log_lifecycle.yml --vault-password-file=.vault_password

# OR with environment variables
export AMT_TEST_PASSWORD="your_password"
ansible-playbook test_log_lifecycle.yml
```

## Test Password Selection

Test passwords should contain irregular symbols and special characters to help identify misbehaving code. Characters like `#`, `&`, `<`, `>`, `@`, `$` are particularly useful for testing XML/SOAP encoding and HTTP authentication. The actual test password is stored only in encrypted vault files, never in documentation.
