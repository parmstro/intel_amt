# amt_user - Manage Intel AMT User Accounts

**⚠️ ENTERPRISE MODE ONLY - Does NOT work with Small Business Mode**

## Synopsis

Manage user accounts on Intel AMT systems running in **Enterprise Mode**.

**IMPORTANT:** This module does **NOT** work with Intel AMT Small Business Mode (AMT 10.0.x and earlier). Small Business Mode does not support user management via WSMAN.

For Small Business Mode systems, you must manage users manually via:
- Intel MEBx (press Ctrl+P during boot)
- AMT web interface (if already configured)
- Intel Manageability Commander tool

## Requirements

- Intel AMT **Enterprise Mode** (NOT Small Business Mode)
- AMT firmware that supports WSMAN user management operations
- Current admin credentials

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **host** | string | yes | | AMT management interface IP/hostname |
| **username** | string | yes | | Current admin username for authentication |
| **password** | string | yes | | Current admin password (no_log: true) |
| **port** | integer | no | 16992 | AMT management port |
| **use_tls** | boolean | no | true | Use TLS for connection |
| **verify_ssl** | boolean | no | false | Verify SSL certificates |
| **target_user** | string | yes | | Username to manage |
| **new_password** | string | conditional | | New password (required for state=password_changed) |
| **state** | string | no | present | Desired state: present, absent, password_changed |

## Return Values

| Key | Type | Description |
|-----|------|-------------|
| **changed** | boolean | Whether user was modified |
| **target_user** | string | Username that was managed |
| **state** | string | Final state |
| **msg** | string | Operation result message |

## Examples

### Check AMT Mode Before Use

```yaml
- name: Verify system is Enterprise Mode
  parmstro.intel_amt.amt_host_status:
    host: amt.example.com
    username: admin
    password: "{{ amt_password }}"
  register: status
  
- name: Fail if Small Business Mode
  fail:
    msg: "User management requires Enterprise Mode. This system is Small Business Mode."
  when: "'Small Business' in (status.version | default(''))"
```

### Change Admin Password (Enterprise Mode Only)

```yaml
- name: Update admin password
  parmstro.intel_amt.amt_user:
    host: amt.example.com
    username: admin
    password: "{{ old_password }}"
    port: 16992
    use_tls: true
    target_user: admin
    new_password: "{{ new_password }}"
    state: password_changed
```

## Notes

- **This module will FAIL on Small Business Mode systems** with a clear error message
- Small Business Mode = AMT 10.0.x and earlier firmware
- Enterprise Mode = AMT 11.0+ or systems provisioned in Enterprise Mode
- Use `amt_host_status` to check AMT mode before attempting user management
- For Small Business Mode, manual password rotation via MEBx is required

## Limitations

### Small Business Mode
- ❌ Cannot add users
- ❌ Cannot remove users  
- ❌ Cannot change passwords
- ✅ Must use Intel MEBx (Ctrl+P during boot)

### Enterprise Mode
- ✅ Full user management supported
- ✅ Remote password changes
- ✅ Add/remove users via WSMAN

## See Also

- [amt_host_status](amt_host_status.md) - Query AMT version and mode
- [AMT Mode Compatibility Guide](amt_mode_compatibility.md) - Feature comparison

## Author

parmstro
