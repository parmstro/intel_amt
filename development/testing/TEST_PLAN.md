# Pre-Push Testing Plan

## Test Environment

**Available Systems:**
- c1s2n2: 192.168.254.209 (chassis 1, stack 2, node 2)
- c1s2n3: 192.168.254.210 (chassis 1, stack 2, node 3)

**AMT Version:** 10.0.56 (Small Business Mode)
**Connection:** HTTP port 16992

## Test Checklist

### Phase 1: Credentials & Vault ✓
- [ ] Vault file loads correctly
- [ ] Credentials work with real AMT
- [ ] Environment variable fallback works
- [ ] Missing credentials fail with helpful error

### Phase 2: Core Modules ✓
- [ ] amt_host_status - Query system status
- [ ] amt_power - Query power state
- [ ] amt_system_settings - Query and modify hostname
- [ ] amt_power_policy - Query and modify idle timeout
- [ ] amt_event_log - Retrieve logs
- [ ] amt_log_clear - Clear logs

### Phase 3: Fleet Operations ✓
- [ ] fleet_query_status - Query 2 systems
- [ ] fleet_configure_standard - Apply config to fleet
- [ ] Parallel execution works (throttle)
- [ ] Error handling (continue_on_error)

### Phase 4: Security Validation ✓
- [ ] No passwords in .md files
- [ ] No passwords in .yml files (except encrypted vault)
- [ ] .vault_password in .gitignore
- [ ] Vault files are encrypted

### Phase 5: Documentation ✓
- [ ] README.md examples work
- [ ] vault/README.md instructions work
- [ ] CI/CD examples are correct

## Test Results

Will be filled in during testing...
