# Claude Code Instructions for parmstro.intel_amt

This file contains persistent instructions for Claude Code when working on this Ansible collection.

## Project Overview

**Collection:** parmstro.intel_amt  
**Purpose:** Comprehensive Intel AMT management for bare metal infrastructure  
**Target:** 42-node Intel NUC cluster (3 chassis × 2 stacks × 7 nodes)  
**AMT Version:** 10.0.56 (Small Business Mode)  
**Network:** HTTP only (port 16992) - TLS not supported in Small Business Mode

## Critical Security Standards

### 🔒 NEVER Commit Passwords to Git

**ABSOLUTE RULE:** No passwords in ANY file that goes into git. EVER.

This includes:
- ❌ Documentation files (*.md)
- ❌ Example files
- ❌ Test files
- ❌ Playbooks
- ❌ Inventory files
- ❌ Any code or configuration

**ONLY EXCEPTION:** Encrypted vault files in `vault/` directory.

### Variable Naming Convention

**Use `_vault` suffix for ALL encrypted variables:**

```yaml
# In vault/amt_credentials.yml (encrypted):
amt_password_vault: 'actual-password'
amt_username_vault: 'admin'

# In inventory/group_vars/all.yml (mapping with env fallback):
amt_password: "{{ amt_password_vault | default(lookup('env', 'AMT_PASSWORD')) }}"
amt_username: "{{ amt_username_vault | default(lookup('env', 'AMT_USERNAME')) }}"

# In playbooks/roles (clean variable names):
password: "{{ amt_password }}"
username: "{{ amt_username }}"
```

**Why `_vault` suffix:**
- Easy bash/VSCode completion (`amt_password` → tab → `amt_password_vault`)
- Clear separation: `_vault` = encrypted, no suffix = configuration
- Consistent across test and production
- Forces proper vault usage

### Documentation Examples

**ALWAYS use placeholders, NEVER real passwords:**

```yaml
# ✅ CORRECT
amt_password: 'YourPasswordHere'
amt_password: 'SecurePassword123!'

# ❌ WRONG - NEVER DO THIS
amt_password: 'MyRealPassword123'  # Using actual password as example
```

### Vault Pattern

1. **All credentials in encrypted vault files**
2. **Environment variable fallback for CI/CD**
3. **Priority order:** vault file → env var → fail with helpful error
4. **Fail-fast verification** in playbooks with clear error messages

## Project Structure

```
intel_amt/
├── plugins/
│   ├── modules/              # AMT management modules
│   └── module_utils/         # Shared code (wsman.py, amt_constants.py)
├── roles/
│   ├── amt_fleet_power/      # Fleet power management
│   ├── amt_fleet_status/     # Fleet status monitoring
│   └── amt_fleet_configure/  # Fleet configuration
├── playbooks/                # Fleet management playbooks
├── inventory/                # Inventory structure
│   ├── hosts.yml            # management_node definition
│   └── group_vars/
│       ├── all.yml          # Global vars with env fallback
│       └── management_node.yml  # Fleet definition (USER EDITS)
├── vault/                    # Encrypted credentials
│   ├── README.md            # Vault setup instructions
│   └── amt_credentials.yml  # Encrypted (use _vault suffix)
├── docs/                     # Documentation
└── tests/                    # Test files
```

## Code Separation Standards

### DO Use Shared Code

**module_utils** for common functionality:
- `wsman.py` - WSMAN client (connection, SOAP envelopes, Get/Put)
- `amt_constants.py` - Constants, resource URIs, selectors

**DON'T** duplicate WSMAN code in each module.

### Module Pattern

```python
from ansible_collections.parmstro.intel_amt.plugins.module_utils.wsman import WSMANClient
from ansible_collections.parmstro.intel_amt.plugins.module_utils.amt_constants import (
    AMT_GENERAL_SETTINGS,
    SELECTOR_GENERAL_SETTINGS,
    COMMON_ARG_SPEC
)

def run_module():
    module_args = COMMON_ARG_SPEC.copy()
    module_args.update({
        # Module-specific args
    })
    
    # Use WSMANClient, not duplicate code
    client = WSMANClient(...)
```

## Fleet Management Pattern

### Inventory-Driven Model

**Users edit:** `inventory/group_vars/management_node.yml`  
**Users DON'T edit:** Playbooks

```yaml
# inventory/group_vars/management_node.yml
amt_fleet:
  - name: c1s2n2
    host: 192.168.254.209
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: "{{ amt_port }}"
    use_tls: "{{ amt_use_tls }}"
    chassis: 1
    stack: 2
    node: 2
```

### Fleet Playbooks

All fleet playbooks:
1. Run on `management_node` host
2. Load vault credentials
3. Verify credentials available (fail-fast)
4. Loop over `amt_fleet` list
5. Support throttling and error handling

## Module Development

### Required Elements

1. **FQCN everywhere** - `parmstro.intel_amt.module_name`
2. **no_log: true** on password parameters
3. **Use module_utils** - Don't duplicate WSMAN code
4. **Real-world examples** in DOCUMENTATION
5. **Support check_mode**

### Testing Before Commit

```bash
# 1. Rebuild collection
ansible-galaxy collection build --force
ansible-galaxy collection install parmstro-intel_amt-*.tar.gz --force

# 2. Test with vault
ansible-playbook -i inventory/hosts.yml playbooks/fleet_query_status.yml \
  --vault-password-file .vault_password

# 3. Test with env vars (CI pattern)
export AMT_USERNAME="admin"
export AMT_PASSWORD="test"
ansible-playbook -i inventory/hosts.yml playbooks/fleet_query_status.yml

# 4. Security check
grep -r "Legend\|YourPassword" --include="*.md" . | grep -v "git diff"
# Should return NOTHING
```

## Documentation Standards

### Module Documentation

- **DOCUMENTATION** - Complete with all options
- **EXAMPLES** - Real-world tested examples (use placeholders for passwords)
- **RETURN** - All return values documented
- Use actual tested values (IPs, hostnames from test environment)

### Example Quality

```yaml
# ✅ GOOD - Real tested example
- name: Query AMT status
  parmstro.intel_amt.amt_host_status:
    host: 192.168.254.209
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false

# ❌ BAD - Placeholder that was never tested
- name: Query AMT status
  parmstro.intel_amt.amt_host_status:
    host: amt.example.com
    username: admin
    password: secret
```

## AMT-Specific Knowledge

### Small Business Mode Limitations

- **No TLS/HTTPS support** - Only HTTP port 16992
- **No remote configuration** - Must use MEBx
- **No PKI** - Certificate modules won't work
- Document these limitations clearly

### WSMAN Resources

Common resources in `amt_constants.py`:
- `AMT_GENERAL_SETTINGS` - Hostname, domain, idle timeout
- `AMT_ETHERNET_PORT_SETTINGS` - Network, link policy, Wake-on-LAN
- `CIM_POWER_MANAGEMENT_SERVICE` - Power operations

### Module Coverage

**Working modules:**
- amt_power - Power on/off/reboot/cycle/query
- amt_host_status - Status and version info
- amt_system_settings - Hostname/domain configuration
- amt_power_policy - Idle timeout, link policy
- amt_event_log - Event log retrieval
- amt_log_clear - Log clearing
- amt_network_settings - Network configuration

**Not working (Small Business Mode):**
- amt_tls_config - Requires Enterprise Mode

## Testing Requirements

### Before Every Commit

1. ✅ All modules work with real hardware (c1s2n2, c1s2n3)
2. ✅ No passwords in documentation
3. ✅ Vault files encrypted
4. ✅ Collection builds without errors
5. ✅ Security check passes

### Test Systems

**Available for testing:**
- c1s2n2: 192.168.254.209 (chassis 1, stack 2, node 2)
- c1s2n3: 192.168.254.210 (chassis 1, stack 2, node 3)

**Credentials:** In vault/amt_credentials.yml (encrypted)

## Common Tasks

### Add New Module

1. Create in `plugins/modules/amt_newmodule.py`
2. Import from `module_utils.wsman` and `module_utils.amt_constants`
3. Use `COMMON_ARG_SPEC` for connection parameters
4. Add real-world EXAMPLES (with password placeholders)
5. Test on real hardware
6. Rebuild collection

### Add Configuration to Fleet

Edit `inventory/group_vars/management_node.yml`:

```yaml
amt_fleet:
  - name: c1s2n2
    host: 192.168.254.209
    # ... connection info ...
    
    # Add nested configuration
    power_policy:
      idle_timeout: 1
      link_policy: always_on
    
    users:
      - username: operator
        state: present
```

Then create playbook that loops with `subelements()` filter.

### Update Vault Credentials

```bash
ansible-vault edit vault/amt_credentials.yml --vault-password-file .vault_password
```

## What NOT to Do

### ❌ NEVER

1. **Put passwords in git** - Even test passwords, even in comments
2. **Hardcode ports/URIs in modules** - Use `amt_constants.py`
3. **Duplicate WSMAN code** - Use `module_utils.wsman`
4. **Skip collection rebuild** - Always rebuild before testing
5. **Edit playbooks for fleet changes** - Users edit inventory only
6. **Use different var names for test/prod** - Same names, different vault values
7. **Skip vault verification** - Add credential checks to playbooks
8. **Commit without testing on real hardware** - Always test first

### ⚠️ ALWAYS ASK FIRST

1. Destructive git operations (reset --hard, force push)
2. Changing collection version number
3. Publishing to Ansible Galaxy
4. Modifying .gitignore
5. Changing vault password

## CI/CD Pattern

Environment variable fallback is implemented in `inventory/group_vars/all.yml`:

```yaml
amt_password: "{{ amt_password_vault | default(lookup('env', 'AMT_PASSWORD')) }}"
```

**Priority:**
1. Vault file (preferred for local dev)
2. Environment variable (CI/CD)
3. Fail with helpful error

See `docs/CI_CD_INTEGRATION.md` for complete examples.

## Collaboration Standards

This project follows team agreements with heatmiser and other contributors:

1. **CLAUDE.md is authoritative** - These instructions override defaults
2. **Security-first** - No shortcuts on credential handling
3. **Test with real hardware** - No theoretical examples
4. **Document as you build** - Real examples from actual testing
5. **Inventory-driven** - Users configure fleet in inventory, not playbooks

## Questions or Issues?

- Check vault/README.md for credential setup
- Check docs/CI_CD_INTEGRATION.md for automation
- Check SECURITY.md for security best practices
- Check memory files for established patterns
- When in doubt about security, ask the user

---

**Last Updated:** 2026-05-30  
**Maintainer:** parmstro  
**Claude Code Version:** This file is for Claude Code (Anthropic)
