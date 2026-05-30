# Ansible Collection - parmstro.intel_amt

Intel Active Management Technology (AMT) management collection for Ansible.

Provides modules for managing Intel AMT-enabled systems including Intel NUC, vPro platforms, and other AMT-capable hardware. Built for bare metal provisioning, fleet management, and OpenShift infrastructure automation.

## Description

This collection enables Ansible automation for:
- Power management (on/off/reboot/cycle)
- Boot device control (PXE, HDD, CD)
- System configuration
- Serial-over-LAN console access
- Event log retrieval
- Integration with Red Hat Satellite/Foreman Discovery
- OpenShift bare metal node provisioning

## Tested With

- Intel NUC5i5MYBE with AMT 10.0.56
- Intel AMT firmware 10.0.x and 11.0.x
- Ansible Core 2.14+
- Python 3.9+

## Modules

### parmstro.intel_amt.amt_power

Power management and boot control for AMT systems.

### parmstro.intel_amt.amt_host_status

Retrieve comprehensive system status and information from AMT.

### parmstro.intel_amt.amt_event_log

Retrieve and parse AMT event log entries for monitoring and uptime calculation.

### parmstro.intel_amt.amt_log_clear

Clear AMT event logs for maintenance and troubleshooting.

**Parameters:**
- `host` (required): AMT hostname or IP address
- `username` (required): AMT admin username
- `password` (required): AMT admin password
- `port` (optional): AMT port (default: 16992)
- `use_tls` (optional): Use TLS connection (default: true)
- `verify_ssl` (optional): Verify SSL certificates (default: false)
- `state` (required): Desired state (on, off, reboot, cycle, query)

**amt_power example:**
```yaml
- name: Reboot system via AMT
  parmstro.intel_amt.amt_power:
    host: nuc01.amt.example.com
    username: admin
    password: secretpassword
    port: 16992
    use_tls: false
    state: reboot
```

**amt_host_status example:**
```yaml
- name: Get system information
  parmstro.intel_amt.amt_host_status:
    host: nuc01.amt.example.com
    username: admin
    password: secretpassword
  register: system_info

- name: Display info
  debug:
    msg: "System {{ system_info.system_name }} - BIOS {{ system_info.bios_version }}"
```

### Future Modules (Planned)

- `amt_boot_device`: Control boot device order (PXE, HDD, CD)
- `amt_sol`: Serial-over-LAN console management
- `amt_kvm`: KVM redirection control
- `amt_config`: AMT configuration management
- `amt_user`: AMT user management
- `amt_alarm_clock`: Configure AMT alarm clock for scheduled wake

## Installation

### From Ansible Galaxy (when published)
```bash
ansible-galaxy collection install parmstro.intel_amt
```

### From Source
```bash
git clone https://github.com/parmstro/intel_amt.git
cd intel_amt
ansible-galaxy collection build
ansible-galaxy collection install parmstro-intel_amt-*.tar.gz
```

## Requirements

- Python packages: `requests`, `lxml`
- Network access to AMT management interface (typically port 16992 or 16993)
- AMT enabled and provisioned on target systems

## Example Playbooks

### Power On Fleet
```yaml
- name: Power on NUC fleet
  hosts: nucs
  gather_facts: false
  tasks:
    - name: Power on via AMT
      parmstro.intel_amt.amt_power:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        state: on
```

### PXE Boot for Provisioning
```yaml
- name: Force PXE boot for Satellite provisioning
  hosts: new_nodes
  gather_facts: false
  tasks:
    - name: Set PXE boot and reboot
      parmstro.intel_amt.amt_power:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        state: pxe_once  # Future feature
```

## Use Cases

### Bare Metal OpenShift
- Power management for OpenShift bare metal nodes
- Integration with Metal3/Baremetal Operator
- Automated node provisioning workflow

### Lab Management
- Manage large fleets of Intel NUC systems
- Automated power cycling for testing
- Remote console access for headless systems

### Satellite/Foreman Integration
- Force PXE boot for discovery
- Power control during provisioning
- Post-provision verification

## Development

See CONTRIBUTING.md for development guidelines.

## Hardware Support

### Tested Hardware
- Intel NUC5i5MYBE (AMT 10.0.56)
- Intel NUC generation 5-11 with AMT

### AMT Versions
- AMT 10.0.x (tested)
- AMT 11.0.x (should work)
- AMT 12.0+ (should work)

## Protocol

Uses WS-Management (WSMAN) over HTTP/HTTPS with SOAP/XML messaging and HTTP Digest authentication.

## License

GNU General Public License v3.0 or later

See LICENSE for full text.

## Author

parmstro (@parmstro on GitHub)

Built for NUCLabv3 - a 42-node Intel NUC cluster for OpenShift development.
## AMT Mode Compatibility - Important Notice

### Two Types of Intel AMT

Intel AMT can operate in two different modes with significantly different capabilities:

#### 1. Small Business Mode
- **TLS/HTTPS:** ❌ Not supported
- **Ports:** HTTP only (16992)
- **Setup:** Manual via MEBx
- **Target:** Small business, isolated networks
- **Examples:** Intel NUC5i5MYBE with AMT 10.0.56

#### 2. Enterprise Mode  
- **TLS/HTTPS:** ✅ Fully supported
- **Ports:** HTTP (16992) and HTTPS (16993)
- **Setup:** Remote provisioning or MEBx
- **Target:** Enterprise deployments with PKI
- **Examples:** AMT 11+ systems, Enterprise vPro

### How to Check Your AMT Mode

Boot your system and press **Ctrl+P** to enter Intel MEBx. Look for a **"TLS PKI"** menu:
- ✅ **TLS PKI menu present** = Enterprise Mode (all modules supported)
- ❌ **TLS PKI menu absent** = Small Business Mode (amt_tls_config not supported)

### Module Compatibility

| Module | Small Business | Enterprise |
|--------|----------------|------------|
| amt_power | ✅ | ✅ |
| amt_host_status | ✅ | ✅ |
| amt_event_log | ✅ | ✅ |
| amt_log_clear | ✅ | ✅ |
| amt_network_settings | ✅ | ✅ |
| amt_tls_config | ❌ | ✅ |

**See [AMT Mode Compatibility Guide](docs/amt_mode_compatibility.md) for complete details.**
