# Intel AMT Ansible Collection Documentation

Welcome to the `parmstro.intel_amt` Ansible collection documentation.

## Overview

This collection provides modules for managing Intel Active Management Technology (Intel AMT) enabled systems. It supports remote power management, system status monitoring, event log management, and network configuration for Intel AMT firmware version 10.0.56.

## Use Cases

- **Bare Metal Provisioning**: Power control for PXE boot and OS deployment
- **Infrastructure Automation**: Remote system management without physical access
- **OpenShift/Kubernetes**: Bare metal node lifecycle management
- **Red Hat Satellite/Foreman**: Integration with discovery and provisioning workflows

## Important: AMT Mode Compatibility

Intel AMT operates in different modes with different capabilities. **Check your AMT mode before using the TLS module:**

- ✅ **Enterprise Mode:** All modules supported including TLS/HTTPS
- ⚠️ **Small Business Mode:** Core modules only (no TLS/HTTPS support)

**[→ Read the AMT Mode Compatibility Guide](amt_mode_compatibility.md)**

## Modules

### Core Modules (All AMT Modes)

#### Power Management
- [amt_power](amt_power.md) - Manage power state (on, off, reboot, cycle, query)

#### System Monitoring
- [amt_host_status](amt_host_status.md) - Retrieve comprehensive system status information

#### Event Log Management
- [amt_event_log](amt_event_log.md) - Retrieve and parse AMT event logs
- [amt_log_clear](amt_log_clear.md) - Clear AMT event logs

#### Network Configuration
- [amt_network_settings](amt_network_settings.md) - Configure AMT network settings (DHCP/static IP)

### Enterprise Mode Only

#### Security Configuration
- [amt_tls_config](amt_tls_config.md) - Configure TLS/HTTPS and certificates (IPA/certmonger integration)
  - ⚠️ **Requires:** AMT Enterprise Mode with TLS support
  - ❌ **Not compatible:** Small Business Mode
  - See [Compatibility Guide](amt_mode_compatibility.md)

## Quick Start

### Installation

```bash
ansible-galaxy collection install parmstro.intel_amt
```

### Basic Example

```yaml
---
- name: Manage Intel AMT systems
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Power on a system
      parmstro.intel_amt.amt_power:
        host: nuc01.amt.example.com
        username: admin
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        state: on

    - name: Check system status
      parmstro.intel_amt.amt_host_status:
        host: nuc01.amt.example.com
        username: admin
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      register: status

    - name: Display status
      ansible.builtin.debug:
        var: status
```

### Vault Integration

Store credentials securely using Ansible Vault:

```bash
# Create vault directory
mkdir -p vault

# Create encrypted credentials file
ansible-vault create vault/credentials.yml
```

Content of `vault/credentials.yml`:
```yaml
amt_username: admin
amt_password: your_secure_password
```

Load in playbook:
```yaml
- name: Load AMT credentials
  ansible.builtin.include_vars:
    dir: vault
    ignore_unknown_extensions: true
    extensions:
      - yml
      - yaml
  no_log: true
```

## Requirements

- Ansible >= 2.9
- Python >= 3.6
- Network access to AMT management interface (typically port 16992 or 16993)
- Valid AMT admin credentials

## Tested Platforms

- Intel AMT firmware 10.0.56 build 3002
- Intel NUC5i5MYBE
- Red Hat Enterprise Linux 9
- Ansible 2.16+

## Protocol Details

All modules use the WS-Management (WSMAN) protocol with:
- HTTP Digest Authentication
- SOAP XML envelope format
- Default ports: 16992 (HTTP), 16993 (HTTPS)
- CIM resource URIs for AMT operations

## Support

- **Issues**: Report issues on GitHub
- **License**: GPL-3.0-or-later
- **Author**: parmstro

## See Also

- [Testing Guide](../TESTING.md)
- [Security Guide](../SECURITY.md)
- [Changelog](../CHANGELOG.md)
- [Release Checklist](../RELEASE_CHECKLIST.md)
