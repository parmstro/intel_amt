# Vault Credentials Setup

This directory contains encrypted credential files for AMT management.

## Quick Start

### 1. Create Vault Password File

```bash
# Create vault password file (NOT committed to git)
echo 'YourVaultPasswordHere' > ../.vault_password
chmod 600 ../.vault_password

# Verify it's in .gitignore
grep -q '.vault_password' ../.gitignore || echo '.vault_password' >> ../.gitignore
```

### 2. Create Encrypted Credentials

```bash
# Create new vault file
ansible-vault create amt_credentials.yml --vault-password-file ../.vault_password
```

### 3. Add Your Credentials

When the editor opens, paste this template with your values:

```yaml
---
# AMT Credentials
# Use _vault suffix for all encrypted variables

amt_username_vault: 'admin'
amt_password_vault: 'YourAMTPasswordHere'
```

Save and exit. The file is now encrypted.

## Environment Variable Fallback (CI/CD)

For automated testing where vault files aren't available:

```bash
# Set environment variables
export AMT_USERNAME="admin"
export AMT_PASSWORD="YourTestPassword"

# Run playbook - env vars used as fallback
ansible-playbook -i ../inventory/hosts.yml ../playbooks/fleet_query_status.yml
```

**Priority order:**
1. Vault file (`amt_password_vault`) - **preferred**
2. Environment variable (`AMT_PASSWORD`) - fallback for CI
3. Fails if neither exists

## Security: NO PASSWORDS IN GIT

**NEVER** commit passwords to git, even in documentation or test files.
All credentials must be in encrypted vault files only.
