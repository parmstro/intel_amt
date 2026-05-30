# CI/CD Integration Guide

This collection supports automated testing via environment variable fallback, allowing CI/CD pipelines to run without vault files.

## Credential Loading Priority

The collection loads credentials in this order:

1. **Vault file** (preferred): `vault/amt_credentials.yml`
2. **Environment variables** (fallback): `AMT_USERNAME`, `AMT_PASSWORD`
3. **Fail** if neither is available

This is implemented in `inventory/group_vars/all.yml`:

```yaml
amt_username: "{{ amt_username_vault | default(lookup('env', 'AMT_USERNAME')) }}"
amt_password: "{{ amt_password_vault | default(lookup('env', 'AMT_PASSWORD')) }}"
```

## Local Development (Vault Preferred)

```bash
# Create encrypted vault file
ansible-vault create vault/amt_credentials.yml --vault-password-file .vault_password

# Add credentials:
---
amt_username_vault: 'admin'
amt_password_vault: 'YourPasswordHere'

# Run playbooks
ansible-playbook -i inventory/hosts.yml playbooks/fleet_query_status.yml \
  --vault-password-file .vault_password
```

## CI/CD Pipelines (Environment Variables)

### GitHub Actions

```yaml
name: Test AMT Collection

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install ansible requests lxml
          ansible-galaxy collection build --force
          ansible-galaxy collection install *.tar.gz --force
      
      - name: Run fleet status query
        env:
          AMT_USERNAME: ${{ secrets.AMT_USERNAME }}
          AMT_PASSWORD: ${{ secrets.AMT_PASSWORD }}
        run: |
          ansible-playbook -i inventory/hosts.yml \
            playbooks/fleet_query_status.yml

      - name: Run sanity tests
        run: ansible-test sanity --docker default
```

**Setup GitHub Secrets:**
1. Go to repository Settings → Secrets and variables → Actions
2. Add secrets:
   - `AMT_USERNAME`: `admin`
   - `AMT_PASSWORD`: Your AMT test password

### GitLab CI/CD

```yaml
variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

stages:
  - test

test:collection:
  stage: test
  image: python:3.9
  before_script:
    - pip install ansible requests lxml
    - ansible-galaxy collection build --force
    - ansible-galaxy collection install *.tar.gz --force
  script:
    - |
      export AMT_USERNAME="${CI_AMT_USERNAME}"
      export AMT_PASSWORD="${CI_AMT_PASSWORD}"
      ansible-playbook -i inventory/hosts.yml \
        playbooks/fleet_query_status.yml
  variables:
    CI_AMT_USERNAME: "admin"
  only:
    - merge_requests
    - main
```

**Setup GitLab CI/CD Variables:**
1. Go to Settings → CI/CD → Variables
2. Add variables:
   - `CI_AMT_USERNAME`: `admin` (not protected)
   - `CI_AMT_PASSWORD`: Your AMT test password (**protected**, **masked**)

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        AMT_USERNAME = 'admin'
        AMT_PASSWORD = credentials('amt-password')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install ansible requests lxml
                    ansible-galaxy collection build --force
                    ansible-galaxy collection install *.tar.gz --force
                '''
            }
        }
        
        stage('Test Collection') {
            steps {
                sh '''
                    ansible-playbook -i inventory/hosts.yml \
                      playbooks/fleet_query_status.yml
                '''
            }
        }
    }
    
    post {
        always {
            junit 'test-results/*.xml'
        }
    }
}
```

**Setup Jenkins Credentials:**
1. Manage Jenkins → Manage Credentials
2. Add Secret text credential:
   - ID: `amt-password`
   - Secret: Your AMT test password

### Azure DevOps

```yaml
trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: amt-credentials  # Variable group with AMT_USERNAME, AMT_PASSWORD

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.9'
    displayName: 'Use Python 3.9'

  - script: |
      pip install ansible requests lxml
      ansible-galaxy collection build --force
      ansible-galaxy collection install *.tar.gz --force
    displayName: 'Install dependencies'

  - script: |
      export AMT_USERNAME=$(AMT_USERNAME)
      export AMT_PASSWORD=$(AMT_PASSWORD)
      ansible-playbook -i inventory/hosts.yml \
        playbooks/fleet_query_status.yml
    displayName: 'Run AMT tests'
    env:
      AMT_USERNAME: $(AMT_USERNAME)
      AMT_PASSWORD: $(AMT_PASSWORD)
```

**Setup Azure DevOps Variables:**
1. Pipelines → Library → Variable groups
2. Create group `amt-credentials` with:
   - `AMT_USERNAME`: `admin`
   - `AMT_PASSWORD`: Your AMT password (lock icon = secret)

## Testing Locally with Environment Variables

Simulate CI/CD environment locally:

```bash
# Set environment variables
export AMT_USERNAME="admin"
export AMT_PASSWORD="YourTestPassword"

# Run without vault file
ansible-playbook -i inventory/hosts.yml playbooks/fleet_query_status.yml

# Verify env vars are used
ansible-playbook -i inventory/hosts.yml playbooks/fleet_query_status.yml -vv \
  | grep -A 5 "Verify credentials"
```

## Security Best Practices for CI/CD

### ✅ DO

- Use CI platform's secret management (GitHub Secrets, GitLab CI/CD Variables, etc.)
- Mark password variables as **secret/masked**
- Use protected branches for production credentials
- Rotate test credentials regularly
- Use different credentials for CI vs production
- Limit secret access to specific branches/tags

### ❌ DON'T

- Never echo/print password variables in CI logs
- Never commit `.env` files with credentials
- Never use production credentials in CI
- Never expose secrets in build artifacts
- Never store secrets in public repositories

## Credential Verification

All playbooks include automatic credential verification:

```yaml
- name: Verify credentials are available
  ansible.builtin.assert:
    that:
      - amt_username is defined
      - amt_password is defined
      - amt_username | length > 0
      - amt_password | length > 0
    fail_msg: |
      ERROR: AMT credentials not found!
      
      Option 1 - Vault file (recommended):
        ansible-vault create vault/amt_credentials.yml
      
      Option 2 - Environment variables (CI/CD):
        export AMT_USERNAME="admin"
        export AMT_PASSWORD="YourPasswordHere"
```

This ensures the playbook fails fast with a helpful error message if credentials are missing.

## Troubleshooting CI/CD

### Credentials Not Found

**Error:**
```
ERROR: AMT credentials not found!
```

**Solution:**
```bash
# Verify env vars are set in CI
echo "Username: ${AMT_USERNAME}"
echo "Password: ${AMT_PASSWORD:0:3}***"  # Show first 3 chars only

# Check CI platform secrets are configured
# GitHub: Settings → Secrets
# GitLab: Settings → CI/CD → Variables
# Jenkins: Manage Jenkins → Credentials
```

### Vault File Loading Failed

**Error:**
```
fatal: [localhost]: FAILED! => {"censored": "the output has been hidden..."}
...ignoring
```

**This is normal in CI!** The playbook tries to load the vault file first, fails (because it doesn't exist in CI), then falls back to environment variables. The `ignore_errors: true` allows this graceful fallback.

### Environment Variables Not Expanding

**Problem:** Variables show as `${AMT_PASSWORD}` instead of actual value

**Solution:**
```yaml
# Use proper syntax for your CI platform:

# GitHub Actions
env:
  AMT_PASSWORD: ${{ secrets.AMT_PASSWORD }}

# GitLab
variables:
  AMT_PASSWORD: "${CI_AMT_PASSWORD}"

# Jenkins
environment {
  AMT_PASSWORD = credentials('amt-password')
}
```

## Testing AMT Collection in CI

### Without Real Hardware

```yaml
# Run syntax checks only
- script: ansible-playbook --syntax-check playbooks/*.yml

# Run sanity tests
- script: ansible-test sanity --docker default

# Run unit tests (if available)
- script: pytest tests/unit/ -v
```

### With Real Hardware (Advanced)

If your CI runner has network access to AMT systems:

```yaml
- name: Test against real AMT
  env:
    AMT_USERNAME: ${{ secrets.AMT_TEST_USERNAME }}
    AMT_PASSWORD: ${{ secrets.AMT_TEST_PASSWORD }}
  run: |
    # Update inventory with CI test host
    echo "c1s2n2:" > test_inventory.yml
    echo "  host: ${AMT_TEST_HOST}" >> test_inventory.yml
    
    ansible-playbook -i test_inventory.yml playbooks/fleet_query_status.yml
```

## Example: Complete CI Pipeline

```yaml
name: Full AMT Collection Test

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install ansible-lint ansible
      - run: ansible-lint

  sanity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install ansible
      - run: ansible-test sanity --docker default

  integration:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    env:
      AMT_USERNAME: ${{ secrets.AMT_USERNAME }}
      AMT_PASSWORD: ${{ secrets.AMT_PASSWORD }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install ansible requests lxml
      - run: ansible-galaxy collection build --force
      - run: ansible-galaxy collection install *.tar.gz --force
      - run: ansible-playbook -i inventory/hosts.yml playbooks/fleet_query_status.yml
```

## Support

For CI/CD integration issues:
- Check [vault/README.md](../vault/README.md) for credential setup
- Review [SECURITY.md](../SECURITY.md) for best practices
- Open an issue with CI platform details
