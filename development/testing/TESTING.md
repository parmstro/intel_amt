# Testing Guide for parmstro.intel_amt Collection

Comprehensive testing strategy before publishing to Ansible Galaxy.

## Test Levels

### 1. Unit Tests
Test individual functions and classes in isolation.

```bash
cd tests/unit
pytest plugins/modules/test_amt_power.py -v
```

### 2. Integration Tests
Test modules with real or mocked AMT hardware.

```bash
# With real hardware (requires AMT system and vault)
# First create vault/amt_credentials.yml with your test credentials
ansible-test integration amt_power \
  --inventory /path/to/inventory.yml \
  --vault-password-file .vault_password

# With mock (safe for CI)
ansible-test integration amt_power --docker default
```

### 3. Sanity Tests
Ansible-specific linting and validation.

```bash
ansible-test sanity --docker default
```

### 4. Documentation Tests
Verify module documentation.

```bash
ansible-test sanity --test ansible-doc
```

## Pre-Release Checklist

### Code Quality
- [ ] All unit tests pass
- [ ] All integration tests pass  
- [ ] All sanity tests pass
- [ ] ansible-lint passes
- [ ] Python code follows PEP 8
- [ ] No TODO/FIXME in production code

### Documentation
- [ ] README.md is complete
- [ ] Module DOCUMENTATION is accurate
- [ ] Module EXAMPLES work
- [ ] Module RETURN is documented
- [ ] CHANGELOG.md exists

### Functionality
- [ ] Tested on real AMT hardware
- [ ] Works with AMT 10.0.x
- [ ] Works with HTTP and HTTPS
- [ ] Error handling is robust
- [ ] Check mode works correctly

### Security
- [ ] Passwords are marked no_log
- [ ] SSL verification can be disabled (for self-signed)
- [ ] No secrets in code or tests
- [ ] Authentication failures handled gracefully

### Collection Structure
- [ ] galaxy.yml is valid
- [ ] meta/runtime.yml is correct
- [ ] License file included (GPL-3.0)
- [ ] All required files present

## Running Full Test Suite

```bash
#!/bin/bash
# run_all_tests.sh

set -e

echo "1. Running unit tests..."
pytest tests/unit/ -v

echo "2. Running sanity tests..."
ansible-test sanity --docker default

echo "3. Running integration tests (requires hardware)..."
if [ -n "$AMT_TEST_HOST" ]; then
    ansible-test integration amt_power \
      -e amt_test_host=$AMT_TEST_HOST \
      -e amt_test_pass=$AMT_TEST_PASS
else
    echo "Skipping integration tests (set AMT_TEST_HOST to enable)"
fi

echo "4. Building collection..."
ansible-galaxy collection build

echo "5. Installing and testing built collection..."
ansible-galaxy collection install parmstro-intel_amt-*.tar.gz --force

echo "All tests passed!"
```

## Testing with Real Hardware

### Setup Test Inventory

```yaml
# tests/integration/inventory.yml
all:
  hosts:
    test_nuc:
      amt_host: c1s2n2.amt.parmstrong.ca
      amt_username: "{{ amt_username }}"
      amt_password: "{{ amt_password }}"
      amt_port: 16992
      amt_use_tls: false
```

### Run Integration Tests

```bash
# Option 1: Using vault file (recommended)
ansible-test integration amt_power \
  --inventory tests/integration/inventory.yml \
  --vault-password-file .vault_password

# Option 2: Using environment variables (CI)
export AMT_PASSWORD="YourTestPassword"
export AMT_USERNAME="admin"
ansible-test integration amt_power \
  --inventory tests/integration/inventory.yml \
  -e "amt_password_vault=${AMT_PASSWORD}" \
  -e "amt_username_vault=${AMT_USERNAME}"
```

### Test Destructive Operations

Only enable when safe:

```bash
export AMT_DESTRUCTIVE_TESTS=true
ansible-test integration amt_power
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Test Collection

on: [push, pull_request]

jobs:
  sanity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run sanity tests
        run: ansible-test sanity --docker default

  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/unit/ -v

  build:
    runs-on: ubuntu-latest
    needs: [sanity, unit]
    steps:
      - uses: actions/checkout@v3
      - name: Build collection
        run: ansible-galaxy collection build
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: collection
          path: parmstro-intel_amt-*.tar.gz
```

## Manual Testing Scenarios

### Scenario 1: First-Time Setup
1. Install collection
2. Configure inventory
3. Test query operation
4. Test check mode
5. Test actual power operation

### Scenario 2: Fleet Operations
1. Configure 10+ systems in inventory
2. Run query on all systems
3. Verify serial execution works
4. Test error handling with unreachable host

### Scenario 3: Integration with Satellite
1. Force PXE boot
2. Verify system boots to network
3. Check discovery registration
4. Power cycle after provision

### Scenario 4: Error Conditions
1. Wrong password
2. Network unreachable
3. AMT disabled
4. Invalid parameters
5. Timeout scenarios

## Performance Testing

Test collection performance with fleet operations:

```bash
# Time 42 sequential power queries
time ansible nucs -m parmstro.intel_amt.amt_power \
  -a "host={{ amt_host }} ... state=query"

# With parallelism
time ansible nucs -m parmstro.intel_amt.amt_power \
  -a "host={{ amt_host }} ... state=query" \
  -f 10  # 10 parallel processes
```

## Reporting Issues

Before publishing, test with multiple users and environments. Document any issues found.

## Ready for Galaxy Checklist

- [ ] Version 1.0.0 tagged
- [ ] All tests passing in CI
- [ ] Tested on production hardware
- [ ] Documentation reviewed
- [ ] CHANGELOG.md updated
- [ ] GitHub release created
- [ ] Ready to publish to Galaxy
